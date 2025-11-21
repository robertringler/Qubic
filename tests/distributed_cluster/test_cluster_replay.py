from qsk.distributed.event_log import EventLog
from qsk.distributed.replay import replay
from qsk.distributed.consensus_stub import propose, commit


def test_event_log_replay_and_consensus():
    log = EventLog()
    log.append("join", {"node": "n1"})
    log.append("join", {"node": "n2"})
    events = replay(log)
    assert events[0]["sequence"] == 1
    decided = propose({"n1": 2, "n2": 3})
    commits = commit(["n1", "n2"], decided)
    assert all(v == decided for v in commits.values())
