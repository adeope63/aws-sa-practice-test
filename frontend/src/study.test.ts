import {describe,it,expect} from 'vitest';
import {shuffleCards} from './StudyGuide';
describe('flashcard shuffling',()=>{
 it('preserves cards without mutating the browse pool',()=>{const input=['one','two','three','four'];const shuffled=shuffleCards(input,()=>0);expect(input).toEqual(['one','two','three','four']);expect(shuffled).not.toEqual(input);expect([...shuffled].sort()).toEqual([...input].sort())});
 it('supports an empty or single-card set',()=>{expect(shuffleCards([])).toEqual([]);expect(shuffleCards(['one'])).toEqual(['one'])});
});
