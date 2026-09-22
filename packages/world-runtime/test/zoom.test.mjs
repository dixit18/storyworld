import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  NESTING_RATIO,
  MAX_LIVE_IMAGES,
  zoomScale,
  nestedFraction,
  nestedAlpha,
  seedFor,
  prng,
} from '../src/index.ts';

describe('zoom contract (r=0.5)', () => {
  it('nesting ratio is 0.5 and live budget <= 4', () => {
    assert.equal(NESTING_RATIO, 0.5);
    assert.ok(MAX_LIVE_IMAGES <= 4);
  });
  it('zoomScale goes 1x -> 2x across a phase', () => {
    assert.equal(zoomScale(0), 1);
    assert.equal(zoomScale(1), 2);
    assert.ok(zoomScale(0.5) > 1 && zoomScale(0.5) < 2);
  });
  it('clamps out-of-range phases', () => {
    assert.equal(zoomScale(-1), 1);
    assert.equal(zoomScale(2), 2);
  });
  it('nested successor grows 0.5x -> 1x', () => {
    assert.equal(nestedFraction(0), 0.5);
    assert.equal(nestedFraction(1), 1);
  });
  it('nested alpha fades in across the phase', () => {
    assert.ok(nestedAlpha(0) < nestedAlpha(1));
    assert.ok(nestedAlpha(1) <= 1);
  });
});

describe('deterministic seeds', () => {
  it('seedFor is stable and distinctive', () => {
    const a = seedFor('mahabharata', 'chapter-01-adi-parva', 'adi-01-naimisha');
    assert.equal(a, seedFor('mahabharata', 'chapter-01-adi-parva', 'adi-01-naimisha'));
    assert.notEqual(a, seedFor('mahabharata', 'chapter-01-adi-parva', 'adi-02-snake-sacrifice'));
  });
  it('prng is reproducible and in [0,1)', () => {
    const r1 = prng(42);
    const r2 = prng(42);
    for (let i = 0; i < 20; i++) {
      const v = r1();
      assert.equal(v, r2());
      assert.ok(v >= 0 && v < 1);
    }
  });
});
