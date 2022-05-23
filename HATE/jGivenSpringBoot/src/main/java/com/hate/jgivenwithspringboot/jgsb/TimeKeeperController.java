package com.hate.jgivenwithspringboot.jgsb;

import java.util.concurrent.atomic.AtomicLong;
import java.util.Date;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TimeKeeperController {

    private static final String prefixDate = "Today's date is: %s";
	private final AtomicLong counter = new AtomicLong();

	@GetMapping("/date")
	public TimeKeeper date(@RequestParam(value = "name", defaultValue = "World") String name) {

		Date mDate = new Date();
		return new TimeKeeper(counter.incrementAndGet(), String.format(prefixDate, mDate.toString()));
	}
    
}
