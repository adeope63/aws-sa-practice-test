import {describe,it,expect} from 'vitest';
import {selectAnswer,timeLabel,percentage} from './api';
describe('exam controls',()=>{
 it('replaces single choice and toggles multiple choices without exceeding the required count',()=>{expect(selectAnswer(['a'],'b',1)).toEqual(['b']);expect(selectAnswer(['a'],'b',2)).toEqual(['a','b']);expect(selectAnswer(['a','b'],'c',2)).toEqual(['a','b']);expect(selectAnswer(['a','b'],'a',2)).toEqual(['b'])});
 it('formats persistent countdown and zero correctly',()=>{expect(timeLabel(7800)).toBe('02:10:00');expect(timeLabel(-1)).toBe('00:00:00');expect(timeLabel(61)).toBe('00:01:01')});
 it('distinguishes no data from a real zero score',()=>{expect(percentage(null)).toBe('—');expect(percentage(0)).toBe('0%')});
});
