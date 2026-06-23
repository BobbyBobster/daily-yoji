import datetime

from pydantic import BaseModel, ConfigDict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app import get_read_conn


class YojiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: int
    kanji: str
    reading: str | None = None
    usage: str | None = None
    meaning: str | None = None
    is_wikipedia_link: bool | None = None
    sentence_id: int | None = None


class SentenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: int
    sentence_text: str
    owner: str
    translation_id: int


class TranslationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")
    id: int
    translation_text: str
    owner: str


router = APIRouter()


@router.get("/")
@router.get("/{max_id}")
async def index(
    max_id: int = 2,
    conn: AsyncConnection = Depends(get_read_conn),
) -> list[YojiResponse] | None:
    query = text(
        """
        SELECT id, kanji FROM yojijukugo
        WHERE id < :max_id;"""
    )
    result = await conn.execute(query, {"max_id": max_id})
    rows = result.mappings().fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Yojijukugo not found")
    return [YojiResponse(**row) for row in rows]


@router.get("/yoji/{id_}")
async def yoji(
    id_: int,
    conn: AsyncConnection = Depends(get_read_conn),
) -> YojiResponse:
    cols = (
        "id",
        "kanji",
        "reading",
        "usage",
        "meaning",
        "is_wikipedia_link",
        "sentence_id",
    )
    query = text(
        f"""
        SELECT {', '.join(cols)} FROM yojijukugo
        WHERE id = :id;"""
    )
    result = await conn.execute(query, {"id": id_})
    row = result.mappings().fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Yojijukugo not found")
    return YojiResponse(**row)


@router.get("/yoji/{q}")
async def search_yoji(
    q: str,
    conn: AsyncConnection = Depends(get_read_conn),
) -> list[YojiResponse]:
    query = text(
        """
        SELECT id, kanji FROM yojijukugo
        WHERE kanji = :q;"""
    )
    result = await conn.execute(query, {"q": q})
    rows = result.mappings().fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Yojijukugo not found")
    return [YojiResponse(**row) for row in rows]


# @router.get('/yoji')
# async def search_yoji_with_param():
#     q = request.args.get('q')
#     if q is None:
#         abort(400, description='Missing required query parameter "q"')

#     # Add actual search function
#     return search_yoji(q)


@router.get("/date/{date}")
async def date_string(
    date: datetime.date,
    conn: AsyncConnection = Depends(get_read_conn),
) -> YojiResponse:
    # try:
    #     datetime.date.fromisoformat(date)
    # except ValueError:
    #     raise HTTPException(status_code=422, detail="No datestring given")

    cols = (
        "id",
        "kanji",
        "reading",
        "usage",
        "meaning",
        "is_wikipedia_link",
        "sentence_id",
        "date",
    )
    query = text(
        f"""
        SELECT {', '.join(cols)} FROM yojijukugo
        WHERE date = :date;"""
    )
    result = await conn.execute(query, {"date": date})
    row = result.mappings().fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Yojijukugo not found")
    return YojiResponse(**row)


@router.route("/date/{year}/{month}/{day}")
async def date_url(year: int, month: int, day: int):
    return await date_string(str(datetime.date(year, month, day)))


@router.get("/sentence/{id_}")
async def sentence(
    id_: int,
    conn: AsyncConnection = Depends(get_read_conn),
) -> SentenceResponse:
    cols = ("id", "sentence_text", "owner", "translation_id")

    query = text(
        f"""
        SELECT {', '.join(cols)} FROM sentence
        WHERE id = :id;"""
    )
    result = await conn.execute(query, {"id": id_})
    row = result.mappings().fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Sentence not found")
    return SentenceResponse(**row)


@router.get("/translation/{id_}")
async def translation(
    id_: int,
    conn: AsyncConnection = Depends(get_read_conn),
) -> TranslationResponse:
    query = text(
        """
        SELECT id, translation_text, owner from translation
        WHERE id = :id;"""
    )
    result = await conn.execute(query, {"id": id_})
    row = result.mappings().fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Translation not found")
    return TranslationResponse(**row)
