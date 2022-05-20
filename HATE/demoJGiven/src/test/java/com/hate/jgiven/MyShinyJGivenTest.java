package test.java.com.hate.jgiven;

import org.junit.Test;
import com.tngtech.jgiven.junit.ScenarioTest;

import com.tngtech.jgiven.junit.ScenarioTest;
import com.tngtech.jgiven.Stage;

class GivenSomeState extends Stage<GivenSomeState> {
    public GivenSomeState some_state() {
        return self();
    }
}


class WhenSomeAction extends Stage<WhenSomeAction> {
    public WhenSomeAction some_action() {
        return self();
    }
}


class ThenSomeOutcome extends Stage<ThenSomeOutcome> {
    public ThenSomeOutcome some_outcome() {
        return self();
    }
}

public class MyShinyJGivenTest
        extends ScenarioTest<GivenSomeState, WhenSomeAction, ThenSomeOutcome> {

    @Test
    public void something_should_happen() {
        given().some_state();
        when().some_action();
        then().some_outcome();
    }
}