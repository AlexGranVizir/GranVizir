package com.hate.jgivenwithspringboot.jgsb;

import org.springframework.http.HttpStatus;

import com.tngtech.jgiven.config.AbstractJGivenConfiguration;
import com.hate.jgivenwithspringboot.jgsb.formater.HttpStatusFormatter;

public class FrameConfiguration extends AbstractJGivenConfiguration {

    @Override
    public void configure() {
        setFormatter( HttpStatus.class, new HttpStatusFormatter() );
    }

}
    
