"""add_attempt_type_for_practice_swings

Revision ID: 87efb90c8ffb
Revises: 2e1ac852f393
Create Date: 2026-09-23 10:51:29.533532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87efb90c8ffb'
down_revision: Union[str, None] = '2e1ac852f393'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add attempt_type column with default 'practice'
    op.add_column('attempts', sa.Column('attempt_type', sa.String(length=20), nullable=False, server_default='practice', comment='Type of attempt: practice or submitted'))

    # For existing data, mark all completed attempts as 'submitted' (they were recorded attempts)
    # This assumes existing attempts were meant to be recorded
    op.execute("UPDATE attempts SET attempt_type = 'submitted' WHERE is_correct = TRUE")

    # Add index for query performance (we'll often filter by attempt_type)
    op.create_index(op.f('ix_attempts_attempt_type'), 'attempts', ['attempt_type'], unique=False)


def downgrade() -> None:
    # Remove index
    op.drop_index(op.f('ix_attempts_attempt_type'), table_name='attempts')

    # Remove column
    op.drop_column('attempts', 'attempt_type')
