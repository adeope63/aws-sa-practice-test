"""Local study flashcards and review progress."""
from alembic import op
import sqlalchemy as sa
revision='003'
down_revision='002'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('flashcards',sa.Column('id',sa.String,primary_key=True),sa.Column('domain',sa.Integer,nullable=False),sa.Column('task',sa.String,nullable=False),sa.Column('chapter',sa.Integer,nullable=False),sa.Column('front',sa.String,nullable=False),sa.Column('back',sa.String,nullable=False),sa.Column('services',sa.JSON,nullable=False),sa.Column('source_page',sa.Integer,nullable=False),sa.Column('source_printed_page',sa.Integer,nullable=False),sa.Column('source_note',sa.String,nullable=False),sa.Column('references',sa.JSON,nullable=False),sa.Column('favorite',sa.Boolean,nullable=False),sa.Column('review_count',sa.Integer,nullable=False),sa.Column('remembered_count',sa.Integer,nullable=False),sa.Column('last_reviewed',sa.Float),sa.Column('due_at',sa.Float),sa.Column('interval_days',sa.Integer,nullable=False))
    op.create_index('ix_flashcards_domain','flashcards',['domain'])
    op.create_index('ix_flashcards_chapter','flashcards',['chapter'])
def downgrade():op.drop_table('flashcards')
