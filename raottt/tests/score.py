
import uuid
import math


from ..game import score


def create_empty_score_tracker(gid=None):
    gid = gid or uuid.uuid4().hex
    return score.Score.new(gid)


def test_empty_score():
    gid = uuid.uuid4().hex
    tracker = create_empty_score_tracker(gid)
    assert tracker.gid == gid
    assert len(tracker.teams['Red']) == 0
    assert len(tracker.teams['Blue']) == 0
    no_move = score.Move(0, 0, 0.50)
    assert tracker.previous['Red'] == no_move
    assert tracker.previous['Blue'] == no_move
    assert tracker.value == 0


def test_after_first_move():
    tracker = create_empty_score_tracker()
    pid = uuid.uuid4().hex
    observed_score = tracker.after_move(10, 0.50, None, 'Red', pid)

    expected_score = 0
    expected_score += score.VALUE_MOVE
    expected_score += score.VALUE_INCREASE_SCORE

    assert observed_score == expected_score
    assert tracker.value == expected_score


def test_after_move_that_improves():
    tracker = create_empty_score_tracker()
    pid1 = uuid.uuid4().hex
    pid2 = uuid.uuid4().hex
    _ = tracker.after_move(1, 0.40, None, 'Red', pid1)
    _ = tracker.after_move(2, 0.60, None, 'Blue', pid2)
    observed_score = tracker.after_move(3, 0.60, None, 'Red', pid1)

    expected_score = 0
    expected_score += score.VALUE_MOVE
    expected_score += score.VALUE_INCREASE_SCORE
    expected_score += score.VALUE_BEHIND_TO_AHEAD

    assert expected_score == observed_score


def test_after_move_that_worsens():
    tracker = create_empty_score_tracker()
    pid1 = uuid.uuid4().hex
    pid2 = uuid.uuid4().hex
    _ = tracker.after_move(3, 0.60, None, 'Red', pid1)
    _ = tracker.after_move(2, 0.50, None, 'Blue', pid2)
    observed_score = tracker.after_move(1, 0.40, None, 'Red', pid1)

    expected_score = 0
    expected_score += score.VALUE_MOVE
    expected_score += score.VALUE_LOWER_SCORE
    expected_score += score.VALUE_AHEAD_TO_BEHIND

    assert expected_score == observed_score


def test_after_move_that_wins():
    tracker = create_empty_score_tracker()
    pid1 = uuid.uuid4().hex
    observed_score = tracker.after_move(0, 0.50, 'Red', 'Red', pid1)

    expected_score = 0
    expected_score += score.VALUE_MOVE
    expected_score += score.VALUE_WINNING_MOVE

    assert expected_score == observed_score


def test_score_distribution_one_player():
    tracker = create_empty_score_tracker()
    pid1 = uuid.uuid4().hex

    tracker.after_move(10, 0.50, None, 'Red', pid1)
    work_lst = tracker.post_game('Red', lambda x: x)

    assert len(work_lst) == 1
    assert work_lst[0][1] == score.FACTOR_WIN * tracker.value


def test_score_distribution_two_players():
    tracker = create_empty_score_tracker()
    pid1 = uuid.uuid4().hex
    pid2 = uuid.uuid4().hex

    tracker.after_move(10, 0.50, None, 'Red', pid1)
    tracker.after_move(10, 0.50, None, 'Blue', pid2)

    work_lst = tracker.post_game('Red', lambda x: x)

    assert len(work_lst) == 2
    for pid, score_delta in work_lst:
        if pid == pid1:
            assert score_delta == score.FACTOR_WIN * tracker.value
        if pid == pid2:
            assert score_delta == score.FACTOR_LOSS * tracker.value


def test_score_distribution_two_players_multiple_winners():
    tracker = create_empty_score_tracker()
    pid1 = uuid.uuid4().hex
    pid2 = uuid.uuid4().hex
    pid3 = uuid.uuid4().hex

    tracker.after_move(10, 0.50, None, 'Red', pid1)
    tracker.after_move(10, 0.50, None, 'Red', pid2)
    tracker.after_move(10, 0.50, None, 'Red', pid1)
    tracker.after_move(10, 0.50, None, 'Blue', pid3)

    work_map = dict(tracker.post_game('Red', lambda x: x))
    assert work_map[pid1] == 2 * work_map[pid2]

