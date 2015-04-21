drop table if exists tasks;
create table tasks (
    id integer,
    tutorialtitle text,
    tutorialwebsite text,
    tutorialtypevideo text,
    tutorialtypeaudio text,
    tutorialtypedirections text,
    levelofexperience text,
    knownInformation text,
    sampletutorial text,
    comments text,
	tutorialcollectionreplciations INTEGER  DEFAULT 2,
	tutorialverificationreplications INTEGER  DEFAULT 2,
	tutorialvotingreplications INTEGER  DEFAULT 2,
	desiredSkill text
);

drop table if exists tutorials;
create table tutorials (
	id integer,
    taskid integer,
    title text,
    resource_link text,
    main text,
    comment text,
    assignmentId text,
    hitId text,
    workerId text,
    turkSubmitTo text,
    agree integer,
    disagree integer
);

drop table if exists votes;
create table votes (
    taskid integer,
	tutorial1  text,
	tutorial2  text,
	assignmentId text,
    hitId text,
    workerId text,
    turkSubmitTo text
);






