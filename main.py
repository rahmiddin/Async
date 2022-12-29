from more_itertools import chunked
import asyncio
from aiohttp import ClientSession
from migrations import engine, Session, People, Base
import json


async def get_character(id):
    session = ClientSession()
    response = await session.get(f'https://swapi.dev/api/people/{id}')
    person = await response.json()
    await session.close()
    return person


async def get_people(start, end):
    for id_chunk in chunked(range(start, end), 10):
        coroutines = [get_character(i) for i in id_chunk]
        people = await asyncio.gather(*coroutines)
        for person in people:
            if 'detail' in person:
                pass
            else:
                print(person)
                yield person


async def paste_people(people):
    async with Session() as session:
        people_orm = [People(
            birth_day=data['birth_year'],
            eye_color=data['eye_color'],
            films=data['films'],
            gender=data['gender'],
            hair_color=data['hair_color'],
            height=data['height'],
            homeworld=data['homeworld'],
            mass=data['mass'],
            name=data['name'],
            skin_color=data['skin_color'],
            species=data['species'],
            starships=data['starships'],
            vehicles=data['vehicles']
        ) for data in people]
        session.add_all(people_orm)
        await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
    person_buffer = []
    async for person_data in get_people(1, 3):
        person_buffer.append(person_data)
        if len(person_buffer) >= 10:
            await paste_people(person_buffer)
            person_buffer = []
        if person_buffer:
            await paste_people(person_buffer)
    await engine.dispose()


if __name__ == '__main__':
    print(asyncio.run(main()))