"""Initial schema — creates all SmartAttend tables.

Revision ID: 0001
Revises: None
Create Date: 2024-01-01 00:00:00.000000
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # 1. ENUM TYPES — must be created before the tables that use them    #
    # ------------------------------------------------------------------ #
    verification_method_enum = postgresql.ENUM(
        "qr", "manual", "gps",
        name="verification_method_enum",
        create_type=True,
    )
    verification_method_enum.create(op.get_bind(), checkfirst=True)

    notification_type_enum = postgresql.ENUM(
        "success", "warning", "info", "error",
        name="notification_type_enum",
        create_type=True,
    )
    notification_type_enum.create(op.get_bind(), checkfirst=True)

    # ------------------------------------------------------------------ #
    # 2. roles                                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    # ------------------------------------------------------------------ #
    # 3. users                                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------ #
    # 4. user_roles                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )

    # ------------------------------------------------------------------ #
    # 5. departments — depends on faculty_profiles (FK added later)      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        # head_faculty_id FK added after faculty_profiles is created
        sa.Column("head_faculty_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_departments_code", "departments", ["code"], unique=True)

    # ------------------------------------------------------------------ #
    # 6. faculty_profiles                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "faculty_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("employee_id", sa.String(50), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("designation", sa.String(100), nullable=False),
        sa.Column("specialization", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("joined_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_faculty_profiles_user_id", "faculty_profiles", ["user_id"], unique=True)
    op.create_index("ix_faculty_profiles_employee_id", "faculty_profiles", ["employee_id"], unique=True)

    # Now add the deferred FK from departments.head_faculty_id -> faculty_profiles.id
    op.create_foreign_key(
        "fk_departments_head_faculty_id",
        "departments", "faculty_profiles",
        ["head_faculty_id"], ["id"],
        ondelete="SET NULL",
    )

    # ------------------------------------------------------------------ #
    # 7. students                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enrollment_number", sa.String(50), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.Column("batch_year", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(10), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_students_user_id", "students", ["user_id"], unique=True)
    op.create_index("ix_students_enrollment_number", "students", ["enrollment_number"], unique=True)
    op.create_index("ix_students_dept_semester", "students", ["department_id", "semester"])
    op.create_index("ix_students_batch", "students", ["batch_year"])

    # ------------------------------------------------------------------ #
    # 8. courses                                                          #
    # ------------------------------------------------------------------ #
    op.create_table(
        "courses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("credit_hours", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_courses_code", "courses", ["code"], unique=True)

    # ------------------------------------------------------------------ #
    # 9. academic_sessions                                                #
    # ------------------------------------------------------------------ #
    op.create_table(
        "academic_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # ------------------------------------------------------------------ #
    # 10. enrollments                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("academic_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("academic_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("student_id", "course_id", "academic_session_id", name="uq_enrollment"),
    )
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"])
    op.create_index("ix_enrollments_course_id", "enrollments", ["course_id"])

    # ------------------------------------------------------------------ #
    # 11. course_faculty_assignments                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "course_faculty_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("faculty_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("academic_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("academic_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("faculty_id", "course_id", "academic_session_id", name="uq_cfa"),
    )
    op.create_index("ix_cfa_faculty_id", "course_faculty_assignments", ["faculty_id"])
    op.create_index("ix_cfa_course_id", "course_faculty_assignments", ["course_id"])

    # ------------------------------------------------------------------ #
    # 12. attendance_sessions                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        "attendance_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("faculty_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("faculty_profiles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("academic_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("academic_sessions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False, server_default="Attendance Session"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("location_lat", sa.Float(), nullable=True),
        sa.Column("location_lng", sa.Float(), nullable=True),
        sa.Column("location_radius_meters", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("gps_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_att_session_course_active", "attendance_sessions", ["course_id", "is_active"])
    op.create_index("ix_att_session_faculty", "attendance_sessions", ["faculty_id"])

    # ------------------------------------------------------------------ #
    # 13. qr_tokens                                                       #
    # ------------------------------------------------------------------ #
    op.create_table(
        "qr_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("attendance_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_qr_tokens_token", "qr_tokens", ["token"], unique=True)
    op.create_index("ix_qr_token_session_active", "qr_tokens", ["session_id", "is_used"])
    op.create_index("ix_qr_token_expires", "qr_tokens", ["expires_at"])

    # ------------------------------------------------------------------ #
    # 14. attendance_records                                              #
    # ------------------------------------------------------------------ #
    op.create_table(
        "attendance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("attendance_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("attendance_sessions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("students.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("qr_token_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("qr_tokens.id", ondelete="SET NULL"), nullable=True),
        sa.Column("marked_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("is_present", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "verification_method",
            sa.Enum("qr", "manual", "gps", name="verification_method_enum", create_type=False),
            nullable=False,
            server_default="qr",
        ),
        sa.Column("student_lat", sa.Float(), nullable=True),
        sa.Column("student_lng", sa.Float(), nullable=True),
        sa.Column("distance_meters", sa.Float(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("is_edited", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("edit_reason", sa.Text(), nullable=True),
        sa.Column("edited_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("attendance_session_id", "student_id", name="uq_attendance_record"),
    )
    op.create_index("ix_att_record_student", "attendance_records", ["student_id"])
    op.create_index("ix_att_record_session", "attendance_records", ["attendance_session_id"])

    # ------------------------------------------------------------------ #
    # 15. notifications                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("success", "warning", "info", "error", name="notification_type_enum", create_type=False),
            nullable=False,
            server_default="info",
        ),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_user_id", "notifications", ["user_id"])

    # ------------------------------------------------------------------ #
    # 16. audit_logs                                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=False),
        sa.Column("resource_id", sa.String(100), nullable=True),
        sa.Column("old_value", postgresql.JSONB(), nullable=True),
        sa.Column("new_value", postgresql.JSONB(), nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])

    # ------------------------------------------------------------------ #
    # 17. password_reset_tokens                                           #
    # ------------------------------------------------------------------ #
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index("ix_password_reset_tokens_token", "password_reset_tokens", ["token"], unique=True)


def downgrade() -> None:
    # Drop tables in reverse dependency order
    op.drop_table("password_reset_tokens")
    op.drop_table("audit_logs")
    op.drop_table("notifications")
    op.drop_table("attendance_records")
    op.drop_table("qr_tokens")
    op.drop_table("attendance_sessions")
    op.drop_table("course_faculty_assignments")
    op.drop_table("enrollments")
    op.drop_table("academic_sessions")
    op.drop_table("courses")
    op.drop_table("students")

    # Drop the deferred FK before dropping departments
    op.drop_constraint("fk_departments_head_faculty_id", "departments", type_="foreignkey")
    op.drop_table("faculty_profiles")
    op.drop_table("departments")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")

    # Drop enum types last
    op.execute("DROP TYPE IF EXISTS verification_method_enum")
    op.execute("DROP TYPE IF EXISTS notification_type_enum")
