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
    budget text,
    blacklist text,
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
    turkSubmitTo text
);

drop table if exists verifications;
create table verifications (
	id integer,
    taskid integer,
	tutorialid  integer,
    overallAcceptance text,
	meetsFormat text,
	meetsDesiredLevel text,
	meetsDesiredSkillRequired text,	
    hitId text,
    workerId text,
    turkSubmitTo text
);

drop table if exists votes;
create table votes (
	id integer,
    taskid integer,
	tutorial1id  integer,
	tutorial2id  integer,
    hitId text,
    workerId text,
    turkSubmitTo text
);






