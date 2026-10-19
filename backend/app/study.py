import json,time
from pathlib import Path
from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Flashcard,SessionLocal
from .blueprint import TASKS
router=APIRouter(prefix='/api/study-guide',tags=['Study guide'])
DATA_FILE=Path(__file__).with_name('study_cards.json')
TEXT_FILE=Path(__file__).resolve().parents[2]/'output/text/AWS SAA-C03 Study Guide - Ben Piper and David Clinton.txt'
def study_session():
    with SessionLocal() as db:yield db
def source_data():return json.loads(DATA_FILE.read_text())
def seed_flashcards(db):
    data=source_data()
    assert len(data['cards'])==100
    assert len({c['id'] for c in data['cards']})==100
    assert {c['task'] for c in data['cards']}==set(TASKS)
    for item in data['cards']:
        assert item['domain']==int(item['task'][0]) and 1<=item['source_page']<=477
        current=db.get(Flashcard,item['id'])
        if current:
            for k,v in item.items():setattr(current,k,v)
        else:db.add(Flashcard(**item))
    db.commit()
def card_data(c):
    return {k:getattr(c,k) for k in ['id','domain','task','chapter','front','back','services','source_page','source_printed_page','source_note','references','favorite','review_count','remembered_count','last_reviewed','due_at','interval_days']}
@router.get('')
def overview(db:Session=Depends(study_session)):
    data=source_data();cards=list(db.scalars(select(Flashcard)))
    return dict(source=data['source'],chapters=[{**chapter,'cards':sum(c.chapter==chapter['id'] for c in cards)} for chapter in data['chapters']],total=len(cards),reviewed=sum(c.review_count>0 for c in cards),favorites=sum(c.favorite for c in cards),due=sum(c.due_at is None or c.due_at<=time.time() for c in cards),remembered=sum(c.interval_days>0 for c in cards),text_available=TEXT_FILE.is_file(),text_url='/api/study-guide/text')
@router.get('/text')
def download_text():
    if not TEXT_FILE.is_file():raise HTTPException(404,'Extracted study guide is unavailable on this installation')
    return FileResponse(TEXT_FILE,media_type='text/plain; charset=utf-8',filename=TEXT_FILE.name)
@router.get('/flashcards')
def flashcards(domain:int=0,chapter:int=0,task:str='',search:str='',collection:str='all',db:Session=Depends(study_session)):
    if collection not in ['all','due','new','favorites']:raise HTTPException(422,'Unknown flashcard collection')
    cards=list(db.scalars(select(Flashcard).order_by(Flashcard.id)))
    if domain:cards=[c for c in cards if c.domain==domain]
    if chapter:cards=[c for c in cards if c.chapter==chapter]
    if task:cards=[c for c in cards if c.task==task]
    if search:cards=[c for c in cards if search.lower() in (c.front+' '+c.back+' '+' '.join(c.services)).lower()]
    if collection=='due':cards=[c for c in cards if c.due_at is None or c.due_at<=time.time()]
    if collection=='new':cards=[c for c in cards if c.review_count==0]
    if collection=='favorites':cards=[c for c in cards if c.favorite]
    return {'total':len(cards),'cards':[card_data(c) for c in cards]}
def get_card(db,cid):
    card=db.get(Flashcard,cid)
    if not card:raise HTTPException(404,'Flashcard not found')
    return card
@router.post('/flashcards/{cid}/favorite')
def favorite(cid:str,db:Session=Depends(study_session)):
    card=get_card(db,cid);card.favorite=not card.favorite;db.commit();return card_data(card)
class Review(BaseModel):rating:str
@router.post('/flashcards/{cid}/review')
def review(cid:str,body:Review,db:Session=Depends(study_session)):
    if body.rating not in ['again','got_it']:raise HTTPException(422,'Choose again or got_it')
    card=get_card(db,cid);card.review_count+=1;card.last_reviewed=time.time()
    if body.rating=='again':card.interval_days=0;card.due_at=time.time()+60
    else:
        card.remembered_count+=1;card.interval_days=min(30,max(1,card.interval_days*2));card.due_at=time.time()+card.interval_days*86400
    db.commit();return card_data(card)
