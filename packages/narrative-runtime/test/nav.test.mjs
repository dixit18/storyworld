import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { stepIndex } from '../src/index.ts';

describe('scene navigation (loop closure)', () => {
  it('steps forward and back within range', () => {
    assert.equal(stepIndex(0, 1, 12), 1);
    assert.equal(stepIndex(5, -1, 12), 4);
    assert.equal(stepIndex(3, 0, 12), 3);
  });
  it('wraps around both ends', () => {
    assert.equal(stepIndex(11, 1, 12), 0);
    assert.equal(stepIndex(0, -1, 12), 11);
  });
});
