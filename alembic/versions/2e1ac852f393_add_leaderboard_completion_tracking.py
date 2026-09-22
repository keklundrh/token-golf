"""add_leaderboard_completion_tracking

Revision ID: 2e1ac852f393
Revises: c9a8d5ac1f93
Create Date: 2026-09-22 14:18:59.043336

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e1ac852f393'
down_revision: Union[str, None] = 'c9a8d5ac1f93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add leaderboard completion tracking columns:
    - sessions.course_total_holes: Number of holes in the course (denormalized from courses.yaml)
    - session_participants.holes_completed: Running count of completed challenges
    - session_participants.course_completed_at: Timestamp when user finished all holes
    - Index for efficient completion filtering
    """
    # Add course_total_holes to sessions table
    op.add_column('sessions', sa.Column('course_total_holes', sa.Integer(), nullable=False, server_default='5'))

    # Add completion tracking to session_participants table
    op.add_column('session_participants', sa.Column('holes_completed', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('session_participants', sa.Column('course_completed_at', sa.DateTime(), nullable=True))

    # Add index for leaderboard queries (session_id, holes_completed, course_completed_at)
    op.create_index(
        'ix_session_participants_completion',
        'session_participants',
        ['session_id', 'holes_completed', 'course_completed_at'],
        unique=False
    )


def downgrade() -> None:
    """
    Remove leaderboard completion tracking.
    """
    # Drop index
    op.drop_index('ix_session_participants_completion', table_name='session_participants')

    # Drop columns from session_participants
    op.drop_column('session_participants', 'course_completed_at')
    op.drop_column('session_participants', 'holes_completed')

    # Drop column from sessions
    op.drop_column('sessions', 'course_total_holes')
