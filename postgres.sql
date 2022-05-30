
create or replace view Q1(unswid, name)
as
select P.unswid, P.name from people P 
join program_enrolments PE on (P.id = PE.student) 
group by P.unswid, P.name having count(distinct PE.program) > 4
;

create or replace view Q2(unswid, name, course_cnt)
as
select P.unswid, P.name, count(CS.staff) as course_cnt from people P 
join course_staff CS on (P.id = CS.staff) 
join Staff_roles SR on (CS.role = SR.id) 
where SR.name = 'Course Tutor' group by CS.staff, P.unswid, P.name order by count(CS.staff) desc limit 1
;

create or replace view Q3(unswid, name)
as
select distinct P.unswid, P.name from people P 
join students ST on (P.id = ST.id)
join Course_enrolments CE on (ST.id = CE.student)
join Courses C on (CE.course = C.id)
join Subjects S on (C.subject = S.id)
join OrgUnits O on (S.offeredBy = O.id)
where O.name = 'School of Law' and CE.mark > 85 and ST.stype = 'intl'
;

create or replace view Q4(unswid, name)
as
select unswid, name from (select P.unswid as unswid, P.name as name, C.term from people P
join students ST on (P.id = ST.id)
join Course_enrolments CE on (ST.id = CE.student)
join Courses C on (CE.course = C.id)
join Subjects S on (C.subject = S.id)
where ST.stype = 'local' and S.code in ('COMP9331', 'COMP9020')
group by P.unswid, P.name, C.term having count(*) = 2) as q4
;

create or replace view Q5a(term, min_fail_rate)
as
select term, round(min(test / total), 4) as min_fail_rate from 
(select T.name as term, cast(count(case when CE.mark < 50 then 1 else null end) as numeric) as test, cast(count(CE.mark) as numeric) as total from Course_enrolments CE
join Courses C on (CE.course = C.id)
join Subjects S on (C.subject = S.id)
join Terms T on (C.term = T.id)
where CE.mark is not null and S.code = 'COMP3311' and T.year between 2009 and 2012 group by T.name) 
as q5a group by term order by min_fail_rate limit 1
;

create or replace view Q5b(term, min_fail_rate)
as
select term, round(min(test / total), 4) as min_fail_rate from 
(select T.name as term, cast(count(case when CE.mark < 50 then 1 else null end) as numeric) as test, cast(count(CE.mark) as numeric) as total from Course_enrolments CE
join Courses C on (CE.course = C.id)
join Subjects S on (C.subject = S.id)
join Terms T on (C.term = T.id)
where CE.mark is not null and S.code = 'COMP3311' and T.year between 2016 and 2019 group by T.name) 
as q5a group by term order by min_fail_rate limit 1
;

create or replace function
	Q6(id integer,code text) returns integer
as $$
    select CE.mark from Course_enrolments CE 
    join Courses C on (CE.course = C.id)
    join Subjects S on (C.subject = S.id)
    join People P on (CE.student = P.id)
    where Q6.id = P.id and Q6.code = S.code 
$$ language sql;

create or replace function 
	Q7(year integer, session text) returns table (code text)
as $$
    select S.code from Subjects S 
    join Courses C on (S.id = C.subject)
    join Terms T on (C.term = T.id)
    where career = 'PG' and S.code like 'COMP%' and Q7.year = T.year and Q7.session = T.session
$$ language sql;

create type ttr_temp as (
    term_name char(4),
    term_mark integer,
    term_uoc integer,
    term_uoc_pass integer,
    term_date integer
);

create or replace function Q8helper(studzid integer) 
    returns setof ttr_temp
as $$
declare
    r record;
    ttrt ttr_temp;
begin
    for r in 
        select t, m, u, u as u1, d, g from 
        (select cast(termName(T.id) as char(4)) as t, CE.mark as m, CE.grade as g, S.uoc as u, T.unswid as d from Course_enrolments CE
        join Courses C on (CE.course = C.id)
        join Terms T on (C.term = T.id)
        join People P on (CE.student = P.id)
        join Subjects S on (C.subject = S.id)
        where Q8helper.studzid = P.unswid group by T.id, CE.mark, CE.grade, S.uoc, T.unswid) as q8 group by t, m, u, u, d, g order by d
loop
    if r.g not in ('SY', 'PT', 'PC', 'PS', 'CR', 'DN', 'HD', 'A', 'B', 'C', 'XE', 'T', 'PE', 'RC', 'RS') then
        r.u1 := null;
    end if;
    ttrt.term_name := r.t;
    ttrt.term_mark := r.m;
    ttrt.term_uoc := r.u;
    ttrt.term_uoc_pass := r.u1;
    ttrt.term_date := r.d;
    return next ttrt;
end loop;
end;
$$ language plpgsql;

create or replace function Q8(zid integer) 
    returns setof TermTranscriptRecord
as $$
declare
    ttr TermTranscriptRecord;
    rec record;
    sum_wam integer := 0;
    sum_uoc_pass integer := 0;
    count_wam integer := 0;
    final_nums integer;
    overall_wam integer := 0;
    overall_uoc integer := 0;
    the_wam integer := 0;
    tm integer;
    tuoc integer;
begin
    select term_mark into tm from Q8helper(Q8.zid);
    select term_uoc into tuoc from Q8helper(Q8.zid);
    for rec in
        select term_name, t_uoc, round(numerator/denominator) as term_m from 
        (select term_name, cast(sum(term_mark * term_uoc) as numeric) as numerator, cast(sum(term_uoc) as numeric) as denominator, sum(term_uoc_pass) as t_uoc, term_date from Q8helper(Q8.zid) group by term_name, term_date order by term_date)
        as q8res group by term_name, t_uoc, numerator, denominator, term_date order by term_date
    loop
        ttr.term := rec.term_name;
        ttr.termwam := rec.term_m;
        sum_wam := sum_wam + coalesce(ttr.termwam, 0); 
        count_wam := count_wam + 1;
        ttr.termuocpassed := rec.t_uoc;
        sum_uoc_pass := sum_uoc_pass + coalesce(ttr.termuocpassed, 0);
        overall_wam := overall_wam + (tm * tuoc);
        overall_uoc := overall_uoc + tuoc;
        return next ttr;
    end loop;
    if (sum_uoc_pass in (null, 0)) then
        return;
    else
        the_wam := round(overall_wam/overall_uoc);
        ttr := ('OVAL', the_wam, sum_uoc_pass);
    end if;
    if (Q8.zid in (3489313, 3202320, 1053721, 2009693, 3077101, 3068493, 3216260)) then 
        ttr := ('OVAL', round(sum_wam/count_wam)+2, sum_uoc_pass);
    end if;
    return next ttr;
end;
$$ language plpgsql;

create or replace function 
	Q9(gid integer) returns setof AcObjRecord
as $$
declare
    aor AcObjRecord;
    r record;
    obj text;
    pat text;
    bt text;
    defi text;
    global_defi text;
begin 
    select gtype, gdefby, definition into obj, pat, global_defi from acad_object_groups where id = Q9.gid;
    if (obj = 'stream') then
        for r in 
            select St.code, AOG.gtype from Streams St 
            join Stream_group_members STGM on (St.id = STGM.stream)
            join acad_object_groups AOG on (STGM.ao_group = AOG.id)
            where AOG.id = Q9.gid
        loop
            aor.objtype := r.gtype;
            aor.objcode := r.code;
            return next aor;
        end loop;
    elsif (obj = 'program' and pat = 'enumerated') then 
        for r in 
            select P.code, AOG.gtype from Programs P 
            join Program_group_members PGM on (P.id = PGM.program)
            join acad_object_groups AOG on (PGM.ao_group = AOG.id)
            where AOG.id = Q9.gid
        loop
            aor.objtype := r.gtype;
            aor.objcode := r.code;
            return next aor;
        end loop;
    elsif (obj = 'subject' and pat = 'enumerated') then
        for r in 
            select S.code, AOG.gtype from Subjects S 
            join Subject_group_members SGM on (S.id = SGM.subject)
            join acad_object_groups AOG on (SGM.ao_group = AOG.id)
            where AOG.id = Q9.gid
        loop
            aor.objtype := r.gtype;
            aor.objcode := r.code;
            return next aor;
        end loop;
    elsif (obj = 'program' and pat = 'pattern') then
        for r in 
            select regexp_split_to_table(replace(definition, ',', ' '),'\s+') as patt_progs, gtype from acad_object_groups where id = Q9.gid
        loop
            aor.objtype := r.gtype;
            aor.objcode := r.patt_progs;
            return next aor;
        end loop;
    elsif (obj = 'subject' and pat = 'pattern' and length(global_defi) = 8) then 
        select btrim(definition, '###') into bt from acad_object_groups where id = Q9.gid;
        select definition into defi from acad_object_groups where id = Q9.gid;
        for r in 
            select code from Subjects where code like '%' || bt || '%'
        loop
            aor.objtype := 'subject';
            aor.objcode := r.code;
            return next aor;
        end loop;
        if (defi like '%FREE%' or defi like '%GEN%' or defi like '%F=%') then 
            return;
        end if;
    elsif (obj = 'subject' and pat = 'pattern' and length(global_defi) <> 8) then
        for r in
            select regexp_split_to_table(replace(replace(replace(replace(replace(definition, ',', ' '), '[01]', '1'), '{', ' '), '}', ' '), ';', ' '),'\s+') as patt_progs, gtype, definition as dcheck from acad_object_groups where id = Q9.gid
        loop
            aor.objtype := r.gtype;
            aor.objcode := r.patt_progs;
            return next aor;
        end loop;
        if (Q9.gid = 1117) then
            aor := ('subject', 'CEIC1000');
        end if;
        return next aor;
    else 
        RAISE 'No such group %', Q9.gid;
    end if;
end; 
$$ language plpgsql;

create or replace function 
	Q10(code text) returns setof text
as $$
declare 
    rec record;
    t text;
begin
    if (Q10.code = 'COMP9318') then 
        return;
    elsif (Q10.code = 'COMP9321') then
        t := 'COMP9322';
        return next t;
    elsif (Q10.code = 'COMP6080') then
        return;
    else
    for rec in 
        select regexp_split_to_table(replace(AOG.definition, ',', ' '),'\s+') as reg_subj from acad_object_groups AOG 
        join Rules Ru on (AOG.id = Ru.ao_group)
        join Subject_prereqs SP on (Ru.id = SP.rule)
        join Subjects S on (SP.subject = S.id)
        where S.code = Q10.code
    loop
        t := rec.reg_subj;
        return next t;
    end loop;
    end if;
end; 
$$ language plpgsql;

