import os, time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

TEST_DB=Path('/tmp/architect-lab-tests.db')
for suffix in ['', '-wal', '-shm']:
    Path(str(TEST_DB)+suffix).unlink(missing_ok=True)
os.environ['DATABASE_URL']=f'sqlite:///{TEST_DB}'
from app.main import app
from app.models import SessionLocal, Exam, Question, ExamItem
from app.seed import build_bank
from sqlalchemy import select
@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c: yield c

def test_bank():
    b=build_bank()
    assert len(b)==400
    assert len({q['family'] for q in b})==100
    assert {q['task'] for q in b}=={'1.1','1.2','1.3','2.1','2.2','3.1','3.2','3.3','3.4','3.5','4.1','4.2','4.3','4.4'}

def test_mock_hidden_scoring_and_resume(client):
    e=client.post('/api/exams',json={'mode':'mock','simulated':True}).json()
    assert len(e['questions'])==65
    assert 7790<e['deadline']-e['server_time']<=7800
    assert all('scored' not in q and 'correct' not in q and 'explanation' not in q for q in e['questions'])
    assert all('explanation' not in o for q in e['questions'] for o in q['options'])
    resumed=client.get('/api/exams/'+e['id']).json()
    assert resumed['deadline']==e['deadline']
    assert [q['options'] for q in resumed['questions']]==[q['options'] for q in e['questions']]
    q=e['questions'][0]
    assert client.post(f'/api/exams/{e["id"]}/check/{q["id"]}').status_code==403
    with SessionLocal() as db:
        rows=list(db.scalars(select(ExamItem).where(ExamItem.exam_id==e['id'])))
        from collections import Counter
        assert Counter(db.get(Question,r.question_id).domain for r in rows if r.scored)=={1:15,2:13,3:12,4:10}
        for r in rows:
            # Unscored are deliberately wrong; they must not reduce the final score.
            r.selected=db.get(Question,r.question_id).correct if r.scored else []
        db.commit()
    result=client.post('/api/exams/'+e['id']+'/submit').json()
    assert result['score']==100
    assert sum(q['scored'] for q in result['questions'])==50
    assert client.post('/api/exams/'+e['id']+'/submit').json()['score']==100
    assert client.put(f'/api/exams/{e["id"]}/answers/{q["id"]}',json={'selected':[]}).status_code==409

def test_all_scored_distribution(client):
    e=client.post('/api/exams',json={'mode':'mock','simulated':False}).json()
    from collections import Counter
    assert Counter(q['domain'] for q in e['questions'])=={1:20,2:17,3:15,4:13}
    result=client.post('/api/exams/'+e['id']+'/submit').json()
    assert result['score']==0
    assert all(q['scored'] for q in result['questions'])

def test_deadline_cannot_be_extended_by_refresh(client):
    e=client.post('/api/exams',json={'count':1,'minutes':1}).json()
    with SessionLocal() as db:
        ex=db.get(Exam,e['id']);ex.deadline=time.time()-2;db.commit()
    result=client.get('/api/exams/'+e['id']).json()
    assert result['status']=='completed' and result['score']==0
    assert client.put(f'/api/exams/{e["id"]}/answers/{e["questions"][0]["id"]}',json={'selected':['a']}).status_code==409

def test_exact_match_review_and_revision(client):
    e=client.post('/api/exams',json={'mode':'challenge','family':'S01','count':4}).json()
    q=next(q for q in e['questions'] if q['select_count']==2)
    assert client.put(f'/api/exams/{e["id"]}/answers/{q["id"]}',json={'selected':['a'],'flagged':True}).status_code==200
    result=client.post('/api/exams/'+e['id']+'/submit').json()
    assert result['score']==0
    assert q['id'] in [x['id'] for x in client.get('/api/questions?source=wrong&limit=100&search=Temporary%20application%20credentials').json()['questions']]
    e2=client.post('/api/exams',json={'family':'S01','count':4}).json()
    for q2 in e2['questions']:
        with SessionLocal() as db: correct=db.get(Question,q2['id']).correct
        assert client.put(f'/api/exams/{e2["id"]}/answers/{q2["id"]}',json={'selected':correct}).status_code==200
    assert client.post('/api/exams/'+e2['id']+'/submit').json()['score']==100
    assert not {'S01-1','S01-2','S01-3','S01-4'} & {x['id'] for x in client.get('/api/questions?source=wrong&limit=100&search=Temporary%20application%20credentials').json()['questions']}

def test_practice_feedback_and_invalid_inputs(client):
    e=client.post('/api/exams',json={'count':1}).json();q=e['questions'][0]
    assert client.put(f'/api/exams/{e["id"]}/answers/{q["id"]}',json={'selected':['invalid']}).status_code==422
    result=client.post(f'/api/exams/{e["id"]}/check/{q["id"]}').json()
    assert result['questions'][0]['correct']
    assert client.put(f'/api/exams/{e["id"]}/answers/{q["id"]}',json={'selected':['a']}).status_code==409
    assert client.post('/api/exams',json={'task':'9.9'}).status_code==422
    assert client.post('/api/exams',json={'domain':1,'count':1000}).status_code==422

def test_bookmarks_settings_analytics(client):
    first=client.get('/api/questions/S01-1').json()
    result=client.post('/api/questions/S01-1/bookmark').json()
    assert result['bookmarked']!=first['bookmarked']
    assert client.get('/api/questions?source=bookmarks').json()['total']>=1
    assert client.put('/api/settings',json={'theme':'light','daily_goal':30,'timezone':'Asia/Dubai'}).status_code==200
    assert client.get('/api/settings').json()['daily_goal']==30
    assert client.put('/api/settings',json={'theme':'bad','daily_goal':30}).status_code==422
    a=client.get('/api/analytics').json()
    assert a['bank_total']==1117 and a['completed']>=4
    assert a['highest']==100 and len(a['tasks'])==14
    assert sum(d['bank'] for d in a['domains'])==1117
    assert len(client.get('/api/comparisons').json())==12
    assert len(client.get('/api/challenges').json())==10

def test_reviewed_import_explanations_provenance_and_corrections(client):
    from app.book_import import build_import
    b=build_import()
    assert len(b)==400 and sum(len(q['options']) for q in b)==1600
    assert sum(q['eligible'] for q in b)==292
    assert all(q['provenance']['original_options'] and q['references'] for q in b)
    assert all(o['explanation'] for q in b for o in q['options'])
    # Wrong source key fixed and both versions retained.
    q=client.get('/api/questions/H159').json()
    assert q['provenance']['source_key']=='b' and q['correct']==['c']
    assert q['provenance']['original_scenario']
    # A factually wrong option corrected while original remains inspectable.
    q=client.get('/api/questions/H003').json()
    assert 'temporary' in next(o['text'] for o in q['options'] if o['id']=='b')
    assert 'without using credentials' in q['provenance']['original_options'][1]['text']
    q=client.get('/api/questions/H009').json()
    assert q['options'][1]['text']=='AWS Shield Standard'
    # Ambiguous RDS/Aurora choice is not assigned an invented unique answer.
    q=client.get('/api/questions/H197').json()
    assert not q['eligible'] and q['correct']==[]
    data=client.get('/api/questions?collection=howlett').json()
    assert data['total']==400 and data['eligible_total']==292
    assert all('provenance' not in q for q in data['questions'])
    assert client.get('/api/questions?collection=howlett&eligibility=review').json()['total']==108
    assert client.get('/api/questions?collection=original').json()['total']==400

def test_import_is_used_in_exams_and_review_only_items_are_excluded(client):
    e=client.post('/api/exams',json={'mode':'quick','collection':'howlett','count':50}).json()
    assert len(e['questions'])==50 and all(q['id'].startswith('H') for q in e['questions'])
    assert all(q['eligible'] and 'provenance' not in q and 'correct' not in q for q in e['questions'])
    assert client.post('/api/exams',json={'family':'howlett-multiple-valid-managed-relational-services','count':1}).status_code==422
    # Import is stable and doesn't remove progress/bookmarks on reseeding.
    with SessionLocal() as db:
        from app.seed import seed
        db.get(Question,'H003').bookmarked=True;db.commit()
        count=db.query(Exam).count();seed(db)
        assert db.query(Question).count()==1117 and db.get(Question,'H003').bookmarked
        assert db.query(Exam).count()==count

def test_study_guide_flashcard_content_and_filters(client):
    from app.study import source_data
    data=source_data()
    assert len(data['cards'])==100 and len(data['chapters'])==13
    from collections import Counter
    assert Counter(c['domain'] for c in data['cards'])=={1:30,2:26,3:24,4:20}
    assert len({c['task'] for c in data['cards']})==14
    assert all(c['source_page']>=43 and c['source_page']<=416 for c in data['cards'])
    overview=client.get('/api/study-guide').json()
    assert overview['total']==100 and overview['due']==100 and overview['reviewed']==0
    assert overview['text_available']
    assert client.get('/api/study-guide/flashcards?domain=1').json()['total']==30
    assert client.get('/api/study-guide/flashcards?task=3.5').json()['total']==4
    assert client.get('/api/study-guide/flashcards?search=consistency').json()['total']>=1
    assert client.get('/api/study-guide/flashcards?chapter=13').json()['total']>=1
    assert client.get('/api/study-guide/flashcards?collection=bad').status_code==422

def test_flashcard_reviews_favorites_and_reseed_preserve_progress(client):
    from app.models import Flashcard
    from app.study import seed_flashcards
    assert client.post('/api/study-guide/flashcards/FC001/review',json={'rating':'bad'}).status_code==422
    assert client.post('/api/study-guide/flashcards/missing/review',json={'rating':'again'}).status_code==404
    updated=client.post('/api/study-guide/flashcards/FC001/review',json={'rating':'got_it'}).json()
    assert updated['review_count']==1 and updated['remembered_count']==1 and updated['interval_days']==1
    assert 86390<updated['due_at']-time.time()<86410
    assert client.post('/api/study-guide/flashcards/FC001/review',json={'rating':'got_it'}).json()['interval_days']==2
    updated=client.post('/api/study-guide/flashcards/FC001/review',json={'rating':'again'}).json()
    assert updated['interval_days']==0 and updated['review_count']==3 and updated['remembered_count']==2
    assert 50<updated['due_at']-time.time()<=60
    favorite=client.post('/api/study-guide/flashcards/FC001/favorite').json()
    assert favorite['favorite']
    assert client.get('/api/study-guide/flashcards?collection=favorites').json()['cards'][0]['id']=='FC001'
    assert client.get('/api/study-guide/flashcards?collection=new').json()['total']==99
    assert client.get('/api/study-guide').json()['reviewed']==1
    with SessionLocal() as db:
        seed_flashcards(db)
        assert db.get(Flashcard,'FC001').favorite and db.get(Flashcard,'FC001').review_count==3
        assert db.query(Question).count()==1117

def test_extracted_guide_download_has_all_pages_and_answer_sections(client):
    response=client.get('/api/study-guide/text')
    assert response.status_code==200 and 'attachment' in response.headers['content-disposition']
    text=response.text
    import re
    assert len(re.findall(r'^--- PDF page \d+ ---$',text,re.M))==477
    assert 'Answers to Assessment Test' in text and 'Answers to Review Questions' in text
    assert 'Chapter 13' in text

def test_sybex_option_explanations_corrections_and_collection(client):
    from app.sybex_import import build_sybex_import
    b=build_sybex_import()
    assert len(b)==317 and sum(len(q['options']) for q in b)==1279
    assert sum(q['eligible'] for q in b)==235
    assert len({q['id'] for q in b})==317
    assert all(q['references'] and q['provenance']['source_explanation'] for q in b)
    data=client.get('/api/questions?collection=sybex').json()
    assert data['total']==317 and data['eligible_total']==235
    assert all(q['id'].startswith('Y') for q in data['questions'])
    assert client.get('/api/questions?collection=howlett').json()['total']==400
    assert client.get('/api/questions?collection=original').json()['total']==400
    role=client.get('/api/questions/Y02-014').json()
    assert role['correct']==['a'] and role['provenance']['source_key']=='d'
    assert all(o['explanation'] for o in role['options'])
    events=client.get('/api/questions/Y07-001').json()
    assert events['correct']==['a','b','d'] and events['select_count']==3
    # Current origins and S3 consistency prevent grading outdated source assertions.
    for qid in ['Y08-017','Y03-010','Y10-025']:
        q=client.get('/api/questions/'+qid).json()
        assert not q['eligible'] and q['correct']==[]
        assert all(o['explanation'].startswith('Study note.') for o in q['options'])
    duplicate=client.get('/api/questions/Y10-005').json()
    assert not duplicate['eligible'] and duplicate['duplicate_of']=='Y02-020'
    e=client.post('/api/exams',json={'mode':'quick','count':50,'collection':'sybex'}).json()
    assert len(e['questions'])==50 and all(q['eligible'] and q['id'].startswith('Y') for q in e['questions'])
    assert all('correct' not in q and all('explanation' not in o for o in q['options']) for q in e['questions'])
    # The multi-response corrected question is scored using the new key, not the book key.
    multi=client.post('/api/exams',json={'mode':'quick','count':1,'collection':'sybex','family':events['family']}).json()
    eid=multi['id']
    response=client.put(f'/api/exams/{eid}/answers/{events["id"]}',json={'selected':['a','b','d']})
    assert response.status_code==200
    result=client.post(f'/api/exams/{eid}/submit').json()
    assert result['score']==100
