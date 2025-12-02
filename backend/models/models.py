""" These are the model classes that represent the data that is stored in the database tables

There isn't a published naming convention for SQL table names. They are often similar to Python with lowercase and
separated with underscores. Some prefer plural, others stick with singular which is closer to the ORM class.

Primary keys are typically "id". Foreign keys usually include the name of the referenced table with "_id" appended.
Non-key fields typically follow the lowercase convention with multiple words separated by underscores.

Avoid using SQL reserved keywords as table and attribute names. https://www.w3schools.com/sql/sql_ref_keywords.asp

"""
from typing import Optional

from pydantic import field_validator
from sqlmodel import CheckConstraint, Field, Relationship, SQLModel


class GamesHost(SQLModel, table=True):
    __tablename__ = "games_host"
    id: Optional[int] = Field(default=None, primary_key=True)
    games_id: int = Field(default=None, foreign_key="games.id")
    host_id: int = Field(default=None, foreign_key="host.id")


class GamesDisability(SQLModel, table=True):
    __tablename__ = "games_disability"
    id: Optional[int] = Field(default=None, primary_key=True)
    games_id: int = Field(default=None, foreign_key="games.id")
    disability_id: int = Field(default=None, foreign_key="disability.id")


class GamesTeam(SQLModel, table=True):
    __tablename__ = "games_team"
    id: Optional[int] = Field(default=None, primary_key=True)
    games_id: int = Field(default=None, foreign_key="games.id")
    team_id: str = Field(default=None, foreign_key="team.code")


class Games(SQLModel, table=True):
    __tablename__ = "games"
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str
    year: int
    start_date: Optional[str]
    end_date: Optional[str]
    countries: Optional[int]
    events: Optional[int]
    sports: Optional[int]
    participants_m: Optional[int]
    participants_f: Optional[int]
    participants: Optional[int]
    highlights: Optional[str]
    url: Optional[str]

    hosts: list["Host"] = Relationship(back_populates="games", link_model=GamesHost)
    disabilities: list["Disability"] = Relationship(back_populates="games", link_model=GamesDisability)
    teams: list["Team"] = Relationship(back_populates="games", link_model=GamesTeam)

    __table_args__ = (
        CheckConstraint("event_type IN ('winter', 'summer')"),
        CheckConstraint("year BETWEEN 1960 AND 9999")
    )

    # TODO: Add @field_validators here

    # TODO: Add a custom __repr__ or __str__ method here
    # __repr__: Developer-focused. Should return an unambiguous representation of the object, ideally something that
    # could be used to recreate the object. Used by repr(obj).

    # __str__: User-focused. Should return a readable, human-friendly description of the object.
    # Used by str(obj) and print(obj).


class Team(SQLModel, table=True):
    __tablename__ = "team"
    code: str = Field(primary_key=True)  # Not set by the database
    name: str
    region: Optional[str]
    member_type: str
    notes: Optional[str]
    country_id: Optional[str] = Field(default=None, foreign_key="country.id")

    games: list["Games"] = Relationship(back_populates="teams", link_model=GamesTeam)

    __table_args__ = (
        CheckConstraint("member_type IN ('country', 'team', 'dissolved', 'construct')"),
        CheckConstraint("region IN ('Asia', 'Europe', 'Africa', 'America', 'Oceania')")
    )

    @field_validator("member_type", mode="after")
    @classmethod
    def validate_member_type(cls, value: str) -> str:
        allowed = ["country", "team", "dissolved", "construct"]
        if value not in allowed:
            raise ValueError(f"{value} is not in {allowed}")
        return value

    @field_validator("region", mode="after")
    @classmethod
    def validate_region(cls, value: Optional[str]) -> Optional[str]:
        allowed = ["Asia", "Europe", "Africa", "America", "Oceania"]
        if value is not None and value not in allowed:
            raise ValueError(f"{value} is not in {allowed}")
        return value

    def __repr__(self) -> str:
        # Dynamically includes all fields
        field_values = ", ".join(f"{name}={getattr(self, name)!r}" for name in self.__model_fields__.keys())
        return f"{self.__class__.__name__}({field_values})"

    def __str__(self) -> str:
        return f"{self.code} {self.name} is in {self.region} and is a {self.member_type}."


class Disability(SQLModel, table=True):
    __tablename__ = "disability"
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str

    games: list["Games"] = Relationship(back_populates="disabilities", link_model=GamesDisability)


class Host(SQLModel, table=True):
    __tablename__ = "host"
    id: Optional[int] = Field(default=None, primary_key=True)
    place_name: str = Field(unique=True)
    country_id: Optional[int] = Field(default=None, foreign_key="country.id")

    games: list["Games"] = Relationship(back_populates="hosts", link_model=GamesHost)


class Country(SQLModel, table=True):
    __tablename__ = "country"
    id: Optional[int] = Field(default=None, primary_key=True)
    country_name: str
