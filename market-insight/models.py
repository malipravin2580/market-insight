from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    DateTime,
    func
)
from sqlalchemy.orm import relationship, declarative_base
# from geoalchemy2 import Geometry  # uncomment if you need PostGIS support

Base = declarative_base()

class ApmcDetail(Base):
    __tablename__ = "apmc_details"

    id = Column(Integer, primary_key=True, index=True)
    apmc_name = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    subdistrict = Column(String(250), nullable=True)
    state_name = Column(String(100), nullable=True)
    # If using PostGIS, uncomment and ensure geoalchemy2 is installed:
    # location = Column(Geometry("POINT"), nullable=True)

    # back-reference from EnaamRecord
    enam_records = relationship("EnaamRecord", back_populates="apmc_detail")


class EnaamRecord(Base):
    __tablename__ = "enaam_records"

    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(50), nullable=True)
    apmc = Column(String(50), nullable=True)
    apmc_detail_id = Column(
        Integer,
        ForeignKey("apmc_details.id"),
        nullable=True
    )
    apmc_detail = relationship("ApmcDetail", back_populates="enam_records")

    commodity = Column(String(50), nullable=True)
    min_price = Column(Integer, nullable=True)
    modal_price = Column(Integer, nullable=True)
    max_price = Column(Integer, nullable=True)
    commodity_arrivals = Column(Integer, nullable=True)
    commodity_traded = Column(Integer, nullable=True)
    commodity_unit = Column(String(30), nullable=True)

    date = Column(Date, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    ) 