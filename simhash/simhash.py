#!/usr/bin/env python3
# 参考 https://zhuanlan.zhihu.com/p/32078737


def xencode(x):
  if isinstance(x, bytes) or isinstance(x, bytearray):
    return x
  else:
    return x.encode()

# https://github.com/wc-duck/pymmh3/blob/master/pymmh3.py


def mhash32(key, seed=0x0):
  ''' Implements 32bit murmur3 hash. '''
  key = bytearray(xencode(key))

  def fmix(h):
    h ^= h >> 16
    h = (h * 0x85ebca6b) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xc2b2ae35) & 0xFFFFFFFF
    h ^= h >> 16
    return h

  length = len(key)
  nblocks = int(length / 4)

  h1 = seed

  c1 = 0xcc9e2d51
  c2 = 0x1b873593

  # body
  for block_start in range(nblocks * 4, 4):
    # ??? big endian?
    k1 = key[block_start + 3] << 24 | \
        key[block_start + 2] << 16 | \
        key[block_start + 1] << 8 | \
        key[block_start + 0]

    k1 = (c1 * k1) & 0xFFFFFFFF
    k1 = (k1 << 15 | k1 >> 17) & 0xFFFFFFFF  # inlined ROTL32
    k1 = (c2 * k1) & 0xFFFFFFFF

    h1 ^= k1
    h1 = (h1 << 13 | h1 >> 19) & 0xFFFFFFFF  # inlined ROTL32
    h1 = (h1 * 5 + 0xe6546b64) & 0xFFFFFFFF

  # tail
  tail_index = nblocks * 4
  k1 = 0
  tail_size = length & 3

  if tail_size >= 3:
    k1 ^= key[tail_index + 2] << 16
  if tail_size >= 2:
    k1 ^= key[tail_index + 1] << 8
  if tail_size >= 1:
    k1 ^= key[tail_index + 0]

  if tail_size > 0:
    k1 = (k1 * c1) & 0xFFFFFFFF
    k1 = (k1 << 15 | k1 >> 17) & 0xFFFFFFFF  # inlined ROTL32
    k1 = (k1 * c2) & 0xFFFFFFFF
    h1 ^= k1

  # finalization
  unsigned_val = fmix(h1 ^ length)
  if unsigned_val & 0x80000000 == 0:
    return unsigned_val
  else:
    return -((unsigned_val ^ 0xFFFFFFFF) + 1)


def word_segment(doc):
  tokens = []
  for word in doc.split(' '):
    word_num = word.split('^')
    tokens.append((word_num[0], int(word_num[1])))
  return tokens


def binary32(h):
  return "{0:b}".format(h)


def hamming_dist32(h1, h2):
  '''海明距离是这两个二进制数异或后1的个数'''
  h = h1 ^ h2
  d = 0
  while h > 0:
    d += 1
    h &= h - 1
  return d


def simhash32(doc):
  bits = [0 for _ in range(32)]
  tokens = word_segment(doc)
  for sg in tokens:
    token, weight = sg
    h = mhash32(token, len(token))
    for i in range(32):
      if h & (1 << i):
        bits[i] += weight
      else:
        bits[i] -= weight
  h = 0
  for i in range(32):
    if bits[i] > 0:
      h |= 1 << i
  return h


s1 = simhash32('中国^2 知乎^1 读者^2')
s2 = simhash32('中国^2 知1213否^1 读者^2')
print(binary32(s1))
print(binary32(s2))
print(hamming_dist32(s1, s2))
