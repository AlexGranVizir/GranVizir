package com.hate.jgivenwithspringboot.jgsb;

public class TimeKeeper {

	private final long id;
	private final String content;

	public TimeKeeper(long id, String content) {
		this.id = id;
		this.content = content;
	}

	public long getId() {
		return id;
	}

	public String getContent() {
		return content;
	}
}
