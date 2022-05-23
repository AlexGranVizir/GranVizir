package com.hate.jgivenwithspringboot.jgsb;

// jUnit 5
import org.junit.jupiter.api.Test;
import com.tngtech.jgiven.integration.spring.junit5.SimpleSpringScenarioTest;

import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.HttpStatus;
import org.springframework.mock.web.MockServletContext;
import org.springframework.test.context.web.WebAppConfiguration;

import com.tngtech.jgiven.annotation.As;
import com.tngtech.jgiven.annotation.JGivenConfiguration;

@SpringBootTest( classes = { MockServletContext.class, TestContext.class } )
@WebAppConfiguration
@JGivenConfiguration( FrameConfiguration.class )
public class TimeKeeperControllerTest extends SimpleSpringScenarioTest<MyStage> {

    @Test
    public void the_root_path_returns_greetings_from_JGiven() throws Exception {
        when().get( "/" );
        then().the_status_is( HttpStatus.OK )
            .and().the_content_is( "Greetings from JGiven!" );
    }
}