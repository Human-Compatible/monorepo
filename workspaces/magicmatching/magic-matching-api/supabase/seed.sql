
-- COPY public.organization (id, slug, bio) FROM stdin;
-- 1	demo-org	good for testing
-- \.

INSERT INTO public.organization (id, slug, name, bio)
    VALUES
        (1, 'demo-org', 'Demo for All', 'good for testing');

