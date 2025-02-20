CREATE OR REPLACE FUNCTION insert_user(
    p_name VARCHAR,
    p_email VARCHAR,
    p_password_hash VARCHAR,
    p_role VARCHAR
) RETURNS TABLE(userid UUID, name VARCHAR, email VARCHAR, role VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    INSERT INTO public."users" (name, email, passwordhash, role)
    VALUES (p_name, p_email, p_password_hash, p_role)
    RETURNING users.userid, users.name, users.email, users.role;
END;
$$;
