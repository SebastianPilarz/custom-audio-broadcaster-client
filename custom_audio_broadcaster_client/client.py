from dataclasses import dataclass
from os import path as p
import asyncio
import threading
import aiohttp
from typing import Optional
from logger import logger


@dataclass
class AudioUrls:
  hls: str
  rtmp: str
  rtsp: str
  srt: str
  webrtc: str


@dataclass
class Room:
  audioUrls: AudioUrls
  currentClientsNumber: int
  description: str
  maxClientsNumber: int
  path: str
  dataUrl: str
  title: str


class Client:

  def __init__(self, url: str) -> None:
    self.url: str = url
    self._session: Optional[aiohttp.ClientSession] = None

  async def close(self):
    await self._session.close()

  async def fetch_rooms(self) -> list[Room]:
    if self._session is None:
      self._session = aiohttp.ClientSession()
    logger.info(f'Fetching rooms from: {self.url}')
    async with self._session.get(self.url) as resp:
      if resp.status != 200:
        logger.error(f'Response != OK: {resp.status}')
        return []
      rooms_json = (await resp.json())['rooms']
      rooms: list[Room] = []
      for room in rooms_json:
        transformed = {
            key: value
            for key, value in room.items() if key != 'audioUrls'
        }
        transformed['audioUrls'] = AudioUrls(**room['audioUrls'])
        rooms.append(Room(**transformed))
      return rooms

  async def fetch_room_data(self, room: Room) -> str:
    if not self._session:
      self._session = aiohttp.ClientSession()
    if not room or not room.dataUrl:
      logger.error('dataUrl is empty')
      return ''
    logger.info(f'Fetching data from: {room.dataUrl}')
    async with self._session.get(room.dataUrl) as resp:
      if resp.status != 200:
        logger.error(f'Response != OK: {resp.status}')
        return
      return await resp.text()


example_room = Room(
    dataUrl='http://localhost:3000/v1/rooms/test/data',
    audioUrls=AudioUrls(hls='', rtmp='', rtsp='', srt='', webrtc=''),
    currentClientsNumber=0,
    description='This is a test room',
    maxClientsNumber=10,
    path='/test',
    title='Test room',
)
if __name__ == '__main__':

  class App:

    def __init__(self):
      self.client = Client(url='http://localhost:3000/v1/rooms')
      self.rooms: list[Room] = []
      self.current_room_idx = 0
      self.lock = asyncio.Lock()

    async def update_rooms(self):
      # i = 0
      # while True:
      try:
        rooms = await self.client.fetch_rooms()
        async with self.lock:
          self.rooms = rooms
        # print(f'i: {i} - {rooms}')
        # i += 1
      except Exception as e:
        print(e)
      # await asyncio.sleep(5)

    async def update_room_data(self):
      print('Updating room data')
      i = 0
      while True:
        await asyncio.sleep(2)
        try:
          async with self.lock:
            # if self.current_room_idx < len(self.rooms):
            room = self.rooms[self.current_room_idx]
            print(f'ROOM: {room}')
            # room = example_room
            data = await self.client.fetch_room_data(room)
            self.data = data
            print(f'i: {i} - {data}')
          # else:
          #   print('No rooms yet')
          i += 1
        except Exception as e:
          print(e)
      # await c.close()

    def start_updater(self):
      self.loop = asyncio.new_event_loop()
      self.th = threading.Thread(target=self.loop.run_forever, daemon=True)
      self.th.start()
      try:
        fut = asyncio.run_coroutine_threadsafe(self.update_rooms(), self.loop)
        fut.result()
        print('Rooms:', self.rooms)
        fut2 = asyncio.run_coroutine_threadsafe(self.update_room_data(),
                                                self.loop)
        # fut2.result()
        # print('Data:', self.data)
        print('...')
        print(self.loop.is_running())
        print(self.th.is_alive())
      except Exception as e:
        print(e)
      # finally:
      #   self.loop.call_soon_threadsafe(self.loop.stop)
      #   self.th.join()
      #   self.loop.close()

  app = App()
  app.start_updater()
  import time
  while True:
    print('Running')
    time.sleep(5)
