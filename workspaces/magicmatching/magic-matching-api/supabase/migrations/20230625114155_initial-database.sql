--
-- PostgreSQL database dump
--

-- Dumped from database version 15.1
-- Dumped by pg_dump version 15.1 (Debian 15.1-1.pgdg110+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgsodium; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";


--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA "public" OWNER TO "postgres";

--
-- Name: pg_graphql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";


--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";


--
-- Name: pgjwt; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "postgis" WITH SCHEMA "extensions";


--
-- Name: supabase_vault; Type: EXTENSION; Schema: -; Owner: -
--

-- CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";


--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "vector" WITH SCHEMA "extensions";

--
-- Name: organization; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organization (
    id bigint NOT NULL,
    slug text NOT NULL,
    name text,
    bio text,
    meta jsonb
);


ALTER TABLE public.organization OWNER TO postgres;

--
-- Name: organization_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organization_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER TABLE public.organization_id_seq OWNER TO postgres;

--
-- Name: organization_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organization_id_seq OWNED BY public.organization.id;


--
-- Name: person; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.person (
    id bigint NOT NULL,
    organization_id bigint NOT NULL,
    username text NOT NULL,
    location text,
    bio text,
    meta jsonb
);


ALTER TABLE public.person OWNER TO postgres;

--
-- Name: person_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.person_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


-- ALTER TABLE public.person_id_seq OWNER TO postgres;

--
-- Name: person_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.person_id_seq OWNED BY public.person.id;


--
-- Name: person_section; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.person_section (
    id bigint NOT NULL,
    person_id bigint NOT NULL,
    content text,
    token_count integer,
    embedding extensions.vector(1536)
);


ALTER TABLE public.person_section OWNER TO postgres;

--
-- Name: person_section_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.person_section_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.person_section_id_seq OWNER TO postgres;

--
-- Name: person_section_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.person_section_id_seq OWNED BY public.person_section.id;




--
-- Name: organization id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organization ALTER COLUMN id SET DEFAULT nextval('public.organization_id_seq'::regclass);


--
-- Name: person id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person ALTER COLUMN id SET DEFAULT nextval('public.person_id_seq'::regclass);


--
-- Name: person_section id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_section ALTER COLUMN id SET DEFAULT nextval('public.person_section_id_seq'::regclass);




--
-- Name: person_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

-- SELECT pg_catalog.setval('public.person_id_seq', 26, true);


--
-- Name: person_section_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

-- SELECT pg_catalog.setval('public.person_section_id_seq', 24, true);



--
-- Name: organization organization_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organization
    ADD CONSTRAINT organization_pkey PRIMARY KEY (id);


--
-- Name: person person_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person
    ADD CONSTRAINT person_username_key UNIQUE (username);


--
-- Name: person person_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person
    ADD CONSTRAINT person_pkey PRIMARY KEY (id);


--
-- Name: person_section person_section_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_section
    ADD CONSTRAINT person_section_pkey PRIMARY KEY (id);






--
-- Name: person person_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person
    ADD CONSTRAINT person_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organization(id) ON DELETE CASCADE;

--
-- Name: person_section person_section_person_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.person_section
    ADD CONSTRAINT person_section_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.person(id) ON DELETE CASCADE;






--
-- Name: TABLE organization; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.organization TO anon;
GRANT ALL ON TABLE public.organization TO authenticated;
GRANT ALL ON TABLE public.organization TO service_role;


--
-- Name: SEQUENCE organization_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.organization_id_seq TO anon;
GRANT ALL ON SEQUENCE public.organization_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.organization_id_seq TO service_role;


--
-- Name: TABLE person; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.person TO anon;
GRANT ALL ON TABLE public.person TO authenticated;
GRANT ALL ON TABLE public.person TO service_role;


--
-- Name: SEQUENCE person_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.person_id_seq TO anon;
GRANT ALL ON SEQUENCE public.person_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.person_id_seq TO service_role;


--
-- Name: TABLE person_section; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.person_section TO anon;
GRANT ALL ON TABLE public.person_section TO authenticated;
GRANT ALL ON TABLE public.person_section TO service_role;


--
-- Name: SEQUENCE person_section_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.person_section_id_seq TO anon;
GRANT ALL ON SEQUENCE public.person_section_id_seq TO authenticated;
GRANT ALL ON SEQUENCE public.person_section_id_seq TO service_role;




--
-- Name: match_person_sections(extensions.vector, double precision, integer, integer); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.match_person_sections(embedding extensions.vector, match_threshold double precision, match_count integer, min_content_length integer) RETURNS TABLE(username text, content text, similarity double precision)
    LANGUAGE plpgsql
    AS $$
#variable_conflict use_variable
begin
  return query
  select
    person.username,
    person_section.content,
    (person_section.embedding <#> embedding) * -1 as similarity
  from person_section
  join person
    on person_section.person_id = person.id

  -- We only care about sections that have a useful amount of content
  where length(person_section.content) >= min_content_length

  -- The dot product is negative because of a Postgres limitation, so we negate it
  and (person_section.embedding <#> embedding) * -1 > match_threshold

  -- OpenAI embeddings are normalized to length 1, so
  -- cosine similarity and dot product will produce the same results.
  -- Using dot product which can be computed slightly faster.
  --
  -- For the different syntaxes, see https://github.com/pgvector/pgvector
  order by person_section.embedding <#> embedding
  
  limit match_count;
end;
$$;


ALTER FUNCTION public.match_person_sections(embedding extensions.vector, match_threshold double precision, match_count integer, min_content_length integer) OWNER TO postgres;



--
-- Name: FUNCTION match_person_sections(embedding extensions.vector, match_threshold double precision, match_count integer, min_content_length integer); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.match_person_sections(embedding extensions.vector, match_threshold double precision, match_count integer, min_content_length integer) TO anon;
GRANT ALL ON FUNCTION public.match_person_sections(embedding extensions.vector, match_threshold double precision, match_count integer, min_content_length integer) TO authenticated;
GRANT ALL ON FUNCTION public.match_person_sections(embedding extensions.vector, match_threshold double precision, match_count integer, min_content_length integer) TO service_role;


