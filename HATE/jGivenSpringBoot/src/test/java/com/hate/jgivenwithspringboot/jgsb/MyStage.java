package com.hate.jgivenwithspringboot.jgsb;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.ResultActions;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import com.tngtech.jgiven.Stage;
import com.tngtech.jgiven.annotation.BeforeStage;
import com.tngtech.jgiven.annotation.Quoted;
import com.tngtech.jgiven.integration.spring.JGivenStage;

@JGivenStage
public class MyStage extends Stage<MyStage> {

    MockMvc mvc;

    @Autowired
    TimeKeeperController timeKeeperController;

    private ResultActions mvcResult;

    @BeforeStage
    public void setUp() throws Exception {
        mvc = MockMvcBuilders.standaloneSetup( timeKeeperController ).build();
    }

    public MyStage get( @Quoted String path ) throws Exception {
        mvcResult = mvc.perform( MockMvcRequestBuilders.get( path ).accept( MediaType.APPLICATION_JSON ) );
        return this;
    }

    public MyStage the_status_is( HttpStatus status ) throws Exception {
        mvcResult.andExpect( status().is( status.value() ) );
        return this;
    }

    public MyStage the_content_is( @Quoted String content ) throws Exception {
        mvcResult.andExpect( content().string( equalTo( content ) ) );
        return this;
    }
}
