import math, random, time, uuid
from collections import Counter
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import SessionLocal, Question, Exam, ExamItem, Setting
from .blueprint import DOMAINS, TASKS

@asynccontextmanager
async def lifespan(app):
    from alembic.config import Config
    from alembic import command
    from pathlib import Path
    command.upgrade(Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini')), 'head')
    from .seed import seed
    with SessionLocal() as db:
        seed(db)
        from .study import seed_flashcards
        seed_flashcards(db)
    yield
app = FastAPI(title='Architect Lab', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173','http://127.0.0.1:5173'], allow_methods=['GET','POST','PUT'], allow_headers=['Content-Type'])
def session():
    with SessionLocal() as db: yield db

def get_exam(db, eid):
    ex = db.get(Exam, eid)
    if not ex: raise HTTPException(404, 'Exam not found')
    if ex.status == 'active' and ex.deadline and ex.deadline <= time.time(): finish(db, ex)
    return ex

def items(db, eid): return list(db.scalars(select(ExamItem).where(ExamItem.exam_id == eid).order_by(ExamItem.position)))
def finish(db, ex):
    if ex.status == 'completed': return
    rows = items(db, ex.id)
    for row in rows: row.correct = set(row.selected) == set(db.get(Question, row.question_id).correct)
    scored = [r for r in rows if r.scored]
    ex.score = round(100 * sum(r.correct for r in scored) / len(scored), 1)
    ex.status = 'completed'
    ex.completed_at = min(time.time(), ex.deadline) if ex.deadline else time.time()
    db.commit()
def expire(db):
    for ex in db.scalars(select(Exam).where(Exam.status == 'active', Exam.deadline <= time.time())): finish(db, ex)

def qdata(q, reveal=False):
    data = {k:getattr(q,k) for k in ['id','title','scenario','domain','task','services','concepts','difficulty','bookmarked','verification','family','eligible','duplicate_of']}
    data['select_count'] = len(q.correct)
    data['collection'] = q.provenance.get('collection','Original architecture cases')
    data['source_number'] = q.provenance.get('source_number')
    data['options'] = [{k:v for k,v in o.items() if k != 'explanation'} for o in q.options]
    if reveal: data.update(correct=q.correct, explanation=q.explanation, references=q.references, options=q.options, provenance=q.provenance)
    return data

def payload(db, ex):
    rows=[]
    for row in items(db, ex.id):
        q=qdata(db.get(Question,row.question_id), ex.status=='completed' or row.checked)
        q['options']=sorted(q['options'],key=lambda o:row.option_order.index(o['id']))
        q.update(selected=row.selected,flagged=row.flagged,checked=row.checked)
        if ex.status=='completed': q.update(scored=row.scored, is_correct=row.correct)
        rows.append(q)
    return dict(id=ex.id, mode=ex.mode, status=ex.status, deadline=ex.deadline, started_at=ex.started_at, completed_at=ex.completed_at, simulated=ex.simulated, score=ex.score, questions=rows, server_time=time.time())

@app.get('/api/health')
def health(): return {'status':'ok'}
@app.get('/api/blueprint')
def blueprint(): return {'domains': DOMAINS, 'tasks':TASKS}
class Start(BaseModel):
    mode: str = 'quick'
    count: int = Field(10, ge=1, le=1000)
    domain: Optional[int] = Field(None, ge=1, le=4)
    task: Optional[str] = None
    minutes: Optional[int] = Field(None, ge=1, le=600)
    simulated: bool = False
    source: Optional[str] = None
    family: Optional[str] = None
    search: Optional[str] = None
    collection: Optional[str] = None
@app.post('/api/exams')
def start(body:Start, db:Session=Depends(session)):
    if body.mode not in ['mock','quick','domain','challenge','revision']: raise HTTPException(422,'Unknown mode')
    if body.task and body.task not in TASKS: raise HTTPException(422,'Unknown task')
    pool=list(db.scalars(select(Question).where(Question.eligible==True)))
    if body.collection=='howlett': pool=[q for q in pool if q.id.startswith('H')]
    if body.collection=='sybex': pool=[q for q in pool if q.id.startswith('Y')]
    if body.collection=='original': pool=[q for q in pool if not q.provenance.get('source_number')]
    if body.domain: pool=[q for q in pool if q.domain==body.domain]
    if body.task: pool=[q for q in pool if q.task==body.task]
    if body.family: pool=[q for q in pool if q.family==body.family]
    if body.search: pool=[q for q in pool if body.search.lower() in (q.scenario+' '+q.title+' '+' '.join(q.services)).lower()]
    if body.source=='bookmarks': pool=[q for q in pool if q.bookmarked]
    if body.source=='wrong':
        wrong=wrong_ids(db); pool=[q for q in pool if q.id in wrong]
    if body.mode=='mock':
        pool=list(db.scalars(select(Question).where(Question.eligible==True)))
        counts=[15,13,12,10] if body.simulated else [20,17,15,13]
        chosen=[]
        for domain,n in enumerate(counts,1):
            candidates=[q for q in pool if q.domain==domain]
            # Prefer distinct architecture families before reusing perspectives.
            random.shuffle(candidates); seen=set(); unique=[]; related=[]
            for q in candidates:
                if q.family in seen: related.append(q)
                else: unique.append(q); seen.add(q.family)
            chosen.extend((q,True) for q in (unique+related)[:n])
        if body.simulated:
            ids={q.id for q,_ in chosen}; remaining=[q for q in pool if q.id not in ids]
            chosen.extend((q,False) for q in random.sample(remaining,15))
        deadline=time.time()+130*60
    else:
        if len(pool)<body.count: raise HTTPException(422,f'Only {len(pool)} questions match these filters. Choose a smaller count.')
        chosen=[(q,True) for q in random.sample(pool,body.count)]
        deadline=time.time()+body.minutes*60 if body.minutes else None
    random.shuffle(chosen)
    ex=Exam(id=str(uuid.uuid4()),mode=body.mode,started_at=time.time(),deadline=deadline,simulated=body.mode=='mock' and body.simulated)
    db.add(ex); db.flush()
    for pos,(q,scored) in enumerate(chosen):
        order=[o['id'] for o in q.options]; random.shuffle(order)
        db.add(ExamItem(exam_id=ex.id,question_id=q.id,position=pos,option_order=order,selected=[],scored=scored))
    db.commit(); return payload(db,ex)
@app.get('/api/exams')
def history(db:Session=Depends(session)):
    expire(db)
    return [dict(id=e.id,mode=e.mode,status=e.status,started_at=e.started_at,completed_at=e.completed_at,deadline=e.deadline,score=e.score,count=len(items(db,e.id))) for e in db.scalars(select(Exam).order_by(Exam.started_at.desc()))]
@app.get('/api/exams/{eid}')
def read_exam(eid:str, db:Session=Depends(session)): return payload(db,get_exam(db,eid))
class Answer(BaseModel):
    selected: list[str] = []
    flagged: bool = False
@app.put('/api/exams/{eid}/answers/{qid}')
def answer(eid:str,qid:str,body:Answer,db:Session=Depends(session)):
    ex=get_exam(db,eid)
    if ex.status!='active': raise HTTPException(409,'Exam has been submitted')
    row=db.scalar(select(ExamItem).where(ExamItem.exam_id==eid,ExamItem.question_id==qid))
    if not row: raise HTTPException(404,'Question not in this exam')
    q=db.get(Question,qid)
    if len(set(body.selected))!=len(body.selected) or not set(body.selected)<=set(row.option_order) or len(body.selected)>len(q.correct): raise HTTPException(422,'Invalid answer selection')
    if row.checked and set(row.selected)!=set(body.selected): raise HTTPException(409,'Checked answers cannot be changed')
    row.selected=body.selected; row.flagged=body.flagged; db.commit()
    return {'saved':True}
@app.post('/api/exams/{eid}/check/{qid}')
def check(eid:str,qid:str,db:Session=Depends(session)):
    ex=get_exam(db,eid)
    if ex.mode=='mock': raise HTTPException(403,'Feedback is available after mock exam submission')
    row=db.scalar(select(ExamItem).where(ExamItem.exam_id==eid,ExamItem.question_id==qid))
    if not row: raise HTTPException(404,'Question not in this exam')
    row.checked=True; row.correct=set(row.selected)==set(db.get(Question,qid).correct); db.commit()
    return payload(db,ex)
@app.post('/api/exams/{eid}/submit')
def submit(eid:str,db:Session=Depends(session)):
    ex=get_exam(db,eid); finish(db,ex); return payload(db,ex)

def wrong_ids(db):
    # Latest graded attempt determines revision membership.
    latest={}
    for row,ex in db.execute(select(ExamItem,Exam).join(Exam,Exam.id==ExamItem.exam_id).where(Exam.status=='completed').order_by(Exam.completed_at,ExamItem.id)):
        latest[row.question_id]=row.correct
    return {qid for qid,value in latest.items() if not value}
@app.get('/api/questions')
def questions(domain:Optional[int]=None,task:Optional[str]=None,search:str='',source:Optional[str]=None,collection:Optional[str]=None,eligibility:Optional[str]=None,offset:int=0,limit:int=20,db:Session=Depends(session)):
    expire(db)
    qs=list(db.scalars(select(Question).order_by(Question.id)))
    if collection=='howlett': qs=[q for q in qs if q.id.startswith('H')]
    if collection=='sybex': qs=[q for q in qs if q.id.startswith('Y')]
    if collection=='original': qs=[q for q in qs if not q.provenance.get('source_number')]
    if eligibility=='scored': qs=[q for q in qs if q.eligible]
    if eligibility=='review': qs=[q for q in qs if not q.eligible]
    if domain: qs=[q for q in qs if q.domain==domain]
    if task: qs=[q for q in qs if q.task==task]
    if search: qs=[q for q in qs if search.lower() in (q.scenario+' '+q.title+' '+' '.join(q.services)).lower()]
    if source=='bookmarks': qs=[q for q in qs if q.bookmarked]
    if source=='wrong': qs=[q for q in qs if q.id in wrong_ids(db)]
    return {'total':len(qs),'eligible_total':sum(q.eligible for q in qs),'questions':[qdata(q) for q in qs[max(0,offset):max(0,offset)+min(max(limit,1),100)]]}
@app.get('/api/questions/{qid}')
def question(qid:str,db:Session=Depends(session)):
    q=db.get(Question,qid)
    if not q: raise HTTPException(404,'Question not found')
    return qdata(q,True)
@app.post('/api/questions/{qid}/bookmark')
def bookmark(qid:str,db:Session=Depends(session)):
    q=db.get(Question,qid)
    if not q: raise HTTPException(404,'Question not found')
    q.bookmarked=not q.bookmarked; db.commit(); return {'bookmarked':q.bookmarked}
@app.get('/api/settings')
def settings(db:Session=Depends(session)):
    values={s.key:s.value for s in db.scalars(select(Setting))}
    return {'theme':'dark','daily_goal':20,'timezone':'Asia/Dubai',**values}
class SettingsBody(BaseModel):
    theme: str
    daily_goal: int = Field(ge=1,le=400)
    timezone: str = 'Asia/Dubai'
@app.put('/api/settings')
def save_settings(body:SettingsBody,db:Session=Depends(session)):
    if body.theme not in ['dark','light']: raise HTTPException(422,'Invalid theme')
    try: ZoneInfo(body.timezone)
    except Exception: raise HTTPException(422,'Invalid timezone')
    for key,value in body.model_dump().items(): db.merge(Setting(key=key,value=value))
    db.commit(); return body.model_dump()
@app.get('/api/analytics')
def analytics(db:Session=Depends(session)):
    expire(db)
    completed=list(db.scalars(select(Exam).where(Exam.status=='completed').order_by(Exam.completed_at)))
    rows=list(db.execute(select(ExamItem,Question,Exam).join(Question,Question.id==ExamItem.question_id).join(Exam,Exam.id==ExamItem.exam_id).where(Exam.status=='completed')))
    scored=[r for r in rows if r[0].scored]
    attempted=[r for r in rows if r[0].selected]
    tz=ZoneInfo(settings(db)['timezone'])
    today=datetime.now(tz).date()
    days={datetime.fromtimestamp(e.completed_at,tz).date() for e in completed}
    streak=0; cursor=today if today in days else today-timedelta(days=1)
    while cursor in days: streak+=1; cursor-=timedelta(days=1)
    stats=[]
    for d in DOMAINS:
        group=[r for r in scored if r[1].domain==d['id']]
        covered={r[1].id for r in group if r[0].selected}
        stats.append({**d,'attempted':len(group),'correct':sum(bool(r[0].correct) for r in group),'accuracy':round(100*sum(bool(r[0].correct) for r in group)/len(group),1) if group else None,'coverage':len(covered),'bank':db.query(Question).filter_by(domain=d['id']).count()})
    task_stats=[]
    for tid,name in TASKS.items():
        group=[r for r in scored if r[1].task==tid]
        task_stats.append(dict(id=tid,name=name,attempted=len(group),accuracy=round(100*sum(bool(r[0].correct) for r in group)/len(group),1) if group else None))
    accuracy=round(100*sum(bool(r[0].correct) for r in scored)/len(scored),1) if scored else None
    recent_mock=[e for e in completed if e.mode=='mock'][-3:]
    readiness=round(sum(e.score for e in recent_mock)/len(recent_mock),1) if len(recent_mock)>=3 else None
    return dict(total_attempted=len(attempted),completed=len(completed),average=round(sum(e.score for e in completed)/len(completed),1) if completed else None,highest=max((e.score for e in completed),default=None),accuracy=accuracy,streak=streak,readiness=readiness,readiness_note='Mean of your last 3 full mock percentages; a study indicator, not an AWS scaled score or a pass prediction.',domains=stats,tasks=task_stats,progress=[dict(id=e.id,date=datetime.fromtimestamp(e.completed_at,tz).strftime('%d %b'),score=e.score,mode=e.mode) for e in completed],bank_total=db.query(Question).count(),scored_pool=db.query(Question).filter_by(eligible=True).count(),imported_total=sum(bool(q.provenance.get('source_number')) for q in db.scalars(select(Question))),review_only=db.query(Question).filter_by(eligible=False).count(),bookmarks=db.query(Question).filter_by(bookmarked=True).count(),wrong=len(wrong_ids(db)),today_attempted=sum(bool(r[0].selected) for r in rows if datetime.fromtimestamp(r[2].completed_at,tz).date()==today))
@app.get('/api/comparisons')
def comparisons():
    from .learning import COMPARISONS
    return COMPARISONS
@app.get('/api/challenges')
def challenges(db:Session=Depends(session)):
    families=['R01','R05','R14','R17','P09','P17','S12','S21','C06','R10']
    return [qdata(db.get(Question,f'{family}-3')) for family in families]

from .study import router as study_router
app.include_router(study_router)
