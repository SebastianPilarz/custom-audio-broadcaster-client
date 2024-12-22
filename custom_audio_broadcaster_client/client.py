from dataclasses import dataclass
from os import path as p
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

  async def fetch_room_data(self, room: Room):
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
      return await resp.json()
