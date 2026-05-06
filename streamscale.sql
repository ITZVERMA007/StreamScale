--
-- PostgreSQL database dump
--

\restrict fOPvMhfBe32L0NI2WZL90P0NVVBbFblfS8zu1L63NWWYO1GoWDd7b2mgvPVst6o

-- Dumped from database version 15.17
-- Dumped by pg_dump version 15.17

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: jobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.jobs (
    job_id uuid NOT NULL,
    original_filename text NOT NULL,
    input_object_name text NOT NULL,
    status character varying NOT NULL,
    resolutions text[],
    created_at timestamp without time zone,
    completed_at timestamp without time zone
);


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.jobs (job_id, original_filename, input_object_name, status, resolutions, created_at, completed_at) FROM stdin;
d7ddbc7c-3ed9-466d-9c15-0627148545ad	ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	input/d7ddbc7c-3ed9-466d-9c15-0627148545ad_ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	PENDING	{360,720,1080}	2026-04-18 20:25:22.283965	\N
a7ba61cc-21a1-43ce-9038-e9fb62ac1be9	ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	input/a7ba61cc-21a1-43ce-9038-e9fb62ac1be9_ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	PENDING	{360,720,1080}	2026-04-18 20:42:38.955525	\N
f0b77a17-e861-44f3-9510-4a9926067bee	ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	input/f0b77a17-e861-44f3-9510-4a9926067bee_ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	PENDING	{360,720,1080}	2026-04-19 04:40:54.890245	\N
7aeaec89-e17b-4fc2-944b-6bf4e7c19220	ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	input/7aeaec89-e17b-4fc2-944b-6bf4e7c19220_ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	PENDING	{360,720,1080}	2026-04-19 06:54:25.002956	\N
58297122-e868-4160-a961-bcb0049c3583	ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	input/58297122-e868-4160-a961-bcb0049c3583_ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	PENDING	{360,720,1080}	2026-04-19 08:34:22.127442	\N
98f26cbe-1c5d-4c8a-a05f-d68231a0a626	ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	input/98f26cbe-1c5d-4c8a-a05f-d68231a0a626_ccde5262-e385-4905-874c-2fe190f5efff_7102266-hd_1920_1080_30fps.mp4	SUCCESS	{360,720,1080}	2026-04-19 09:02:18.865416	2026-04-19 09:02:35.592578
\.


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (job_id);


--
-- PostgreSQL database dump complete
--

\unrestrict fOPvMhfBe32L0NI2WZL90P0NVVBbFblfS8zu1L63NWWYO1GoWDd7b2mgvPVst6o

