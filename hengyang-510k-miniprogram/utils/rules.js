'use strict';

const SUITS = [
    { symbol: '♦', name: '方块', color: 'red' },
    { symbol: '♣', name: '梅花', color: 'black' },
    { symbol: '♥', name: '红桃', color: 'red' },
    { symbol: '♠', name: '黑桃', color: 'black' }
];
const RANKS = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];
const TYPE_NAMES = { single: '单张', pair: '对子', chainPair: '连对', triplePair: '三带二', tripleChain: '三张连对', rocket: '王炸', four: '地炸', straight510: '正 510K', mixed510: '副 510K' };

function rankLabel(rank) {
    return ({ 11: 'J', 12: 'Q', 13: 'K', 14: 'A', 15: '2', 16: '小王', 17: '大王' })[rank] || String(rank);
}

function makeDeck() {
    const deck = [];
    SUITS.forEach((suit, suitIndex) => RANKS.forEach(rank => deck.push({ id: `${suitIndex}-${rank}`, rank, suit: suitIndex, label: rankLabel(rank), suitSymbol: suit.symbol, color: suit.color })));
    deck.push({ id: 'joker-small', rank: 16, suit: -1, label: '小王', suitSymbol: '★', color: 'red', joker: true });
    deck.push({ id: 'joker-big', rank: 17, suit: -1, label: '大王', suitSymbol: '★', color: 'black', joker: true });
    return deck;
}

function shuffle(deck) {
    for (let i = deck.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
}

function sortHandCards(hand) {
    const rankCounts = new Map();
    hand.forEach(card => rankCounts.set(card.rank, (rankCounts.get(card.rank) || 0) + 1));
    const all510Ranks = [5, 10, 13];
    const has510 = (suit, cards) => cards.some(card => card.suit === suit && card.rank === 5) && cards.some(card => card.suit === suit && card.rank === 10) && cards.some(card => card.suit === suit && card.rank === 13);
    const keyFor = card => {
        if (card.joker) return { tier: 5, rank: card.rank, suit: 0 };
        if (rankCounts.get(card.rank) === 4) return { tier: 4, rank: card.rank, suit: card.suit };
        if (has510(card.suit, hand)) return { tier: 3, rank: card.rank, suit: card.suit };
        if (all510Ranks.includes(card.rank) && all510Ranks.every(rank => hand.some(other => other.rank === rank)) && !has510(card.suit, hand)) return { tier: 2, rank: card.rank, suit: card.suit };
        return { tier: 1, rank: card.rank, suit: card.suit };
    };
    hand.sort((a, b) => {
        const left = keyFor(a), right = keyFor(b);
        return right.tier - left.tier || right.rank - left.rank || right.suit - left.suit;
    });
    return hand;
}

function compareStrength(left, right) {
    const length = Math.max(left?.length || 0, right?.length || 0);
    for (let index = 0; index < length; index++) {
        const a = left?.[index] ?? -1;
        const b = right?.[index] ?? -1;
        if (a !== b) return a > b ? 1 : -1;
    }
    return 0;
}

function canPartitionMixed510(list, groupCount) {
    const byRank = new Map([ [5, []], [10, []], [13, []] ]);
    list.forEach(card => byRank.get(card.rank)?.push(card));
    const used = new Set();
    function search(groupIndex) {
        if (groupIndex === groupCount) return true;
        for (const five of byRank.get(5)) {
            if (used.has(five)) continue;
            for (const ten of byRank.get(10)) {
                if (used.has(ten) || ten.suit === five.suit) continue;
                for (const king of byRank.get(13)) {
                    if (used.has(king) || king.suit === five.suit || king.suit === ten.suit) continue;
                    used.add(five); used.add(ten); used.add(king);
                    if (search(groupIndex + 1)) return true;
                    used.delete(five); used.delete(ten); used.delete(king);
                }
            }
        }
        return false;
    }
    return search(0);
}

function is510Group(group, sameSuit = false) {
    const ranks = new Set(group.map(card => card.rank));
    return group.length === 3 && ranks.size === 3 && [5, 10, 13].every(rank => ranks.has(rank)) && (!sameSuit || new Set(group.map(card => card.suit)).size === 1);
}

function evaluate510(list) {
    if (list.length < 3 || list.length % 3 !== 0 || list.some(card => card.joker)) return null;
    const groupCount = list.length / 3;
    const bySuit = new Map();
    const count = new Map();
    list.forEach(card => {
        if (!bySuit.has(card.suit)) bySuit.set(card.suit, []);
        bySuit.get(card.suit).push(card);
        count.set(card.rank, (count.get(card.rank) || 0) + 1);
    });
    const positiveSuits = [...bySuit.entries()]
        .filter(([, group]) => is510Group(group, true))
        .map(([suit]) => suit)
        .sort((a, b) => b - a);
    if (positiveSuits.length === groupCount && bySuit.size === groupCount) return { type: 'straight510', rank: positiveSuits[0], strength: positiveSuits, groupCount, length: list.length, cards: list };
    if ([5, 10, 13].every(rank => count.get(rank) === groupCount) && canPartitionMixed510(list, groupCount)) return { type: 'mixed510', rank: 0, groupCount, length: list.length, cards: list };
    return null;
}

function evaluateTripleChain(list, count) {
    if (list.length < 10 || list.length % 5 !== 0) return null;
    const groupCount = list.length / 5;
    let bestEnd = -1;
    for (let start = 3; start <= 14 - groupCount + 1; start++) {
        const end = start + groupCount - 1;
        if (Array.from({ length: groupCount }, (_, index) => start + index).every(rank => (count.get(rank) || 0) >= 3)) bestEnd = Math.max(bestEnd, end);
    }
    return bestEnd >= 0 ? { type: 'tripleChain', rank: bestEnd, groupCount, length: list.length, cards: list } : null;
}

function evaluate(cards) {
    if (!cards?.length) return null;
    const list = [...cards].sort((a, b) => a.rank - b.rank || a.suit - b.suit);
    const ranks = list.map(card => card.rank);
    const count = new Map();
    ranks.forEach(rank => count.set(rank, (count.get(rank) || 0) + 1));
    const unique = [...count.keys()].sort((a, b) => a - b);
    if (list.length === 2 && ranks.includes(16) && ranks.includes(17)) return { type: 'rocket', rank: 99, length: 2, cards: list };
    if (list.length === 4 && unique.length === 1 && unique[0] <= 15) return { type: 'four', rank: unique[0], length: 4, cards: list };
    const combo510 = evaluate510(list);
    if (combo510) return combo510;
    if (list.length === 1) return { type: 'single', rank: list[0].rank, length: 1, cards: list };
    if (list.length === 2 && unique.length === 1 && unique[0] !== 15) return { type: 'pair', rank: unique[0], length: 2, cards: list };
    if (list.length >= 4 && list.length % 2 === 0 && unique.length === list.length / 2 && unique.every(rank => count.get(rank) === 2 && rank !== 15) && unique.every((rank, index) => index === 0 || rank === unique[index - 1] + 1)) return { type: 'chainPair', rank: unique[unique.length - 1], length: unique.length, cards: list };
    const tripleChain = evaluateTripleChain(list, count);
    if (tripleChain) return tripleChain;
    if (list.length === 5) {
        const tripleRanks = unique.filter(rank => rank !== 15 && count.get(rank) >= 3);
        if (tripleRanks.length === 1) return { type: 'triplePair', rank: tripleRanks[0], length: 5, cards: list };
    }
    return null;
}

const BOMB_TYPES = ['rocket', 'four', 'straight510', 'mixed510'];

function compareBombs(candidate, previous) {
    // 王炸 > 四张炸 > 正 510K > 副 510K > 一切普通牌型。
    if (candidate.type === 'rocket') return true;
    if (previous.type === 'rocket') return false;
    if (candidate.type === 'four') return previous.type !== 'four' || candidate.rank > previous.rank;
    if (previous.type === 'four') return false;
    if (candidate.type === 'straight510') {
        if (previous.type === 'straight510') return candidate.groupCount > previous.groupCount || (candidate.groupCount === previous.groupCount && compareStrength(candidate.strength, previous.strength) > 0);
        // 正 510K 可以压副 510K，也可以压任意普通牌型。
        return true;
    }
    if (candidate.type === 'mixed510') {
        if (previous.type === 'straight510') return false;
        if (previous.type === 'mixed510') return candidate.groupCount > previous.groupCount;
        // 副 510K 可以压任意普通牌型，但不能压正 510K/四张炸/王炸。
        return true;
    }
    return false;
}

function canBeat(candidate, previous) {
    if (!candidate) return false;
    if (!previous) return true;
    if (BOMB_TYPES.includes(candidate.type) || BOMB_TYPES.includes(previous.type)) return compareBombs(candidate, previous);
    if (candidate.type !== previous.type) return false;
    if (candidate.type === 'tripleChain') return candidate.groupCount === previous.groupCount && candidate.rank > previous.rank;
    return candidate.length === previous.length && candidate.rank > previous.rank;
}

function pointsFor(card) { return card.rank === 5 ? 5 : (card.rank === 10 || card.rank === 13 ? 10 : 0); }
function cardsPoints(cards) { return cards.reduce((sum, card) => sum + pointsFor(card), 0); }

module.exports = { SUITS, RANKS, TYPE_NAMES, rankLabel, makeDeck, shuffle, sortHandCards, evaluate, canBeat, pointsFor, cardsPoints };
