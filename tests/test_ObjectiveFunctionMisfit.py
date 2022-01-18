import pytest
import numpy

from OptClim2 import ObjectiveFunctionMisfit
from test_ObjectiveFunction import TestObjectiveFunction as TOF
from OptClim2 import LookupState
from OptClim2 import OptClimPreliminaryRun, OptClimNewRun


@pytest.fixture
def rundir(tmpdir_factory):
    res = tmpdir_factory.mktemp("of-misfit")
    return res


@pytest.fixture
def resultA():
    return 1000.


class TestObjectiveFunctionMisfit(TOF):
    @pytest.fixture
    def objfun(self):
        return ObjectiveFunctionMisfit

    @pytest.fixture
    def objectiveAvA(self, objectiveA, valuesA):
        o = objectiveA
        try:
            o.get_result(valuesA)
        except OptClimPreliminaryRun:
            pass
        try:
            o.get_result(valuesA)
        except OptClimNewRun:
            pass
        return o

    def test_empty_lookup(self, objectiveA, valuesA):
        # these should all fail because the param set is missing
        with pytest.raises(LookupError):
            objectiveA.state(valuesA)
        with pytest.raises(LookupError):
            objectiveA.set_result(valuesA, resultA)
        with pytest.raises(RuntimeError):
            objectiveA.get_new()

    def test_lookup_parameters_two(self, objectiveA, valuesA, resultA):
        # test what happens when we insert a new value

        # first time we lookup a parameter should raise OptClimPreliminaryRun
        with pytest.raises(OptClimPreliminaryRun):
            objectiveA.get_result(valuesA)
        # the state should be provisional now
        assert objectiveA.state(valuesA) == LookupState.PROVISIONAL
        # a second lookup of the same parameter should get a new exception
        with pytest.raises(OptClimNewRun):
            objectiveA.get_result(valuesA)
        # the state should be new now
        assert objectiveA.state(valuesA) == LookupState.NEW
        # should succeed but return a random value
        r = objectiveA.get_result(valuesA)
        assert isinstance(r, float)
        assert r != resultA
        # attempting to set result should fail because
        # parameter set is in wrong state ('n')
        with pytest.raises(RuntimeError):
            objectiveA.set_result(valuesA, resultA)

    def test_get_new(self, objectiveAvA, valuesA):
        p = objectiveAvA.get_new()
        assert p == valuesA
        # the state should be new now
        assert objectiveAvA.state(valuesA) == LookupState.ACTIVE
        # should fail now because if already consumed it
        with pytest.raises(RuntimeError):
            objectiveAvA.get_new()

    def test_set_result(self, objectiveAvA, valuesA, resultA):
        objectiveAvA.get_new()
        # set the value
        objectiveAvA.set_result(valuesA, resultA)
        # state should be completed
        assert objectiveAvA.state(valuesA) == LookupState.COMPLETED
        # and we should be able to retrieve the value
        assert objectiveAvA.get_result(valuesA) == resultA
        # this should fail because the value is in the wrong
        # state
        with pytest.raises(RuntimeError):
            objectiveAvA.set_result(valuesA, resultA)

    def test_call(self, objectiveAvA, valuesA, resultA):
        return
        objectiveAvA.get_new()
        objectiveAvA.set_result(valuesA, resultA)
        assert objectiveAvA(list(valuesA.values()), numpy.array([])) == resultA
