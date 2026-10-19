"""Track imported sources and safe scored eligibility without replacing history."""
from alembic import op
import sqlalchemy as sa
revision='002'
down_revision='001'
branch_labels=None
depends_on=None
def upgrade():
    op.add_column('questions',sa.Column('eligible',sa.Boolean,nullable=False,server_default=sa.true()))
    op.add_column('questions',sa.Column('duplicate_of',sa.String,nullable=True))
    op.add_column('questions',sa.Column('provenance',sa.JSON,nullable=False,server_default='{}'))
def downgrade():
    with op.batch_alter_table('questions') as batch:
        batch.drop_column('provenance')
        batch.drop_column('duplicate_of')
        batch.drop_column('eligible')
