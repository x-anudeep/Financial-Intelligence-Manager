from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    industry: Mapped[str] = mapped_column(String(120), default="Middle Market")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    periods: Mapped[list["FinancialPeriod"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class FinancialPeriod(Base):
    __tablename__ = "financial_periods"
    __table_args__ = (UniqueConstraint("company_id", "period", name="uq_company_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    period: Mapped[str] = mapped_column(String(40), index=True)
    period_type: Mapped[str] = mapped_column(String(20), default="annual")
    fiscal_year: Mapped[int] = mapped_column(Integer, index=True)

    company: Mapped[Company] = relationship(back_populates="periods")
    metrics: Mapped[list["FinancialMetric"]] = relationship(back_populates="period", cascade="all, delete-orphan")


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"
    __table_args__ = (UniqueConstraint("period_id", "metric_name", name="uq_period_metric"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    period_id: Mapped[int] = mapped_column(ForeignKey("financial_periods.id"), index=True)
    metric_name: Mapped[str] = mapped_column(String(80), index=True)
    value: Mapped[float | None] = mapped_column(Float, nullable=True)

    period: Mapped[FinancialPeriod] = relationship(back_populates="metrics")
