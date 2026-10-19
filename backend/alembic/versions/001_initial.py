"""Create local examination tables."""
from alembic import op
import sqlalchemy as sa
revision = '001'
down_revision = None
branch_labels = None
depends_on = None
def upgrade():
    op.create_table('questions',sa.Column('id',sa.String,primary_key=True),sa.Column('domain',sa.Integer,nullable=False),sa.Column('task',sa.String,nullable=False),sa.Column('family',sa.String,nullable=False),sa.Column('title',sa.String,nullable=False),sa.Column('scenario',sa.String,nullable=False),sa.Column('services',sa.JSON,nullable=False),sa.Column('concepts',sa.JSON,nullable=False),sa.Column('options',sa.JSON,nullable=False),sa.Column('correct',sa.JSON,nullable=False),sa.Column('explanation',sa.String,nullable=False),sa.Column('difficulty',sa.String,nullable=False),sa.Column('references',sa.JSON,nullable=False),sa.Column('verification',sa.String,nullable=False),sa.Column('bookmarked',sa.Boolean,nullable=False))
    op.create_index('ix_questions_domain','questions',['domain'])
    op.create_index('ix_questions_task','questions',['task'])
    op.create_table('exams',sa.Column('id',sa.String,primary_key=True),sa.Column('mode',sa.String,nullable=False),sa.Column('status',sa.String,nullable=False),sa.Column('started_at',sa.Float,nullable=False),sa.Column('deadline',sa.Float),sa.Column('completed_at',sa.Float),sa.Column('simulated',sa.Boolean,nullable=False),sa.Column('score',sa.Float))
    op.create_table('exam_items',sa.Column('id',sa.Integer,primary_key=True),sa.Column('exam_id',sa.String,sa.ForeignKey('exams.id'),nullable=False),sa.Column('question_id',sa.String,sa.ForeignKey('questions.id'),nullable=False),sa.Column('position',sa.Integer,nullable=False),sa.Column('option_order',sa.JSON,nullable=False),sa.Column('selected',sa.JSON,nullable=False),sa.Column('flagged',sa.Boolean,nullable=False),sa.Column('scored',sa.Boolean,nullable=False),sa.Column('checked',sa.Boolean,nullable=False),sa.Column('correct',sa.Boolean))
    op.create_index('ix_exam_items_exam_id','exam_items',['exam_id'])
    op.create_table('settings',sa.Column('key',sa.String,primary_key=True),sa.Column('value',sa.JSON,nullable=False))
def downgrade():
    op.drop_table('settings')
    op.drop_table('exam_items')
    op.drop_table('exams')
    op.drop_table('questions')
