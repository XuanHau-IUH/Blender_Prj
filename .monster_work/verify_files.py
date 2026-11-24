import json
import struct
from pathlib import Path


root = Path(r'D:\Blender\AI\One_Eyed_Monster')


def uint(data, offset, size=4):
    return int.from_bytes(data[offset:offset+size], 'big')


def boxes(data, start=0, end=None):
    end = len(data) if end is None else end
    while start + 8 <= end:
        size, name = struct.unpack_from('>I4s', data, start)
        header = 8
        if size == 1:
            size = uint(data, start+8, 8)
            header = 16
        if size == 0:
            size = end-start
        assert header <= size <= end-start, (name, start, size, end)
        yield name, data[start+header:start+size]
        start += size


def verify_mp4(path):
    data = path.read_bytes()
    container = dict(boxes(data))
    assert b'ftyp' in container and b'mdat' in container
    for atom, track in boxes(container[b'moov']):
        if atom != b'trak':
            continue
        track = dict(boxes(track))
        media = dict(boxes(track[b'mdia']))
        if media[b'hdlr'][8:12] != b'vide':
            continue
        track_head = track[b'tkhd']
        dimension = (uint(track_head, len(track_head)-8) >> 16, uint(track_head, len(track_head)-4) >> 16)
        media_head = media[b'mdhd']
        pos = 20 if media_head[0] == 1 else 12
        duration = uint(media_head,pos+4,8 if media_head[0] == 1 else 4) / uint(media_head,pos)
        samples = dict(boxes(dict(boxes(media[b'minf']))[b'stbl']))
        frames = uint(samples[b'stsz'], 8)
        print(path.name, dimension, 'duration', round(duration, 3), 'frames', frames,
              'fps', round(frames/duration, 2), 'bytes', len(data))
        assert frames >= 24 and frames / duration >= 12 - .01
        return
    raise AssertionError('No video track')


for name in ('Front','Side','Back','Perspective_3-4','Side_Opposite','Clay','Wireframe'):
    path = root / (name + '.png')
    if not path.exists():
        print('Waiting for', path.name)
        continue
    with path.open('rb') as file:
        header = file.read(33)
        assert header[:8] == b'\x89PNG\r\n\x1a\n'
        assert header[12:16] == b'IHDR'
        dimensions = struct.unpack('>II', header[16:24])
        assert dimensions == (3840,2160)
        file.seek(-12,2)
        assert file.read()[4:8] == b'IEND'
    print(path.name, dimensions, 'bytes', path.stat().st_size)

path = root / 'One_Eyed_Monster.glb'
with path.open('rb') as stream:
    signature, version, size = struct.unpack('<4sII', stream.read(12))
    assert signature == b'glTF' and version == 2 and size == path.stat().st_size
    length, name = struct.unpack('<I4s', stream.read(8))
    assert name == b'JSON'
    content = json.load(__import__('io').BytesIO(stream.read(length)))
assert len(content['meshes']) == 15 and len(content['skins']) == 1
assert len(content['skins'][0]['joints']) == 7
tracks = {track['name']:track for track in content['animations']}
assert set(tracks) == {'Idle','Turntable'}
assert sum(channel['target']['path']=='weights' for channel in tracks['Idle']['channels']) == 2
print(path.name, '15 separate meshes, 7 joints, Idle and Turntable, morph weights on both eyelids')

for name in ('Idle','Turntable'):
    path = root / (name + '.mp4')
    if path.exists():
        verify_mp4(path)
    else:
        print('Waiting for', path.name)
