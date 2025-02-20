CREATE OR REPLACE FUNCTION get_user_by_name(p_name VARCHAR)
RETURNS TABLE(userid UUID, name VARCHAR, passwordhash VARCHAR, email VARCHAR, role VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    	SELECT users.userid, users.name, users.passwordhash, users.email, users.role 
    	FROM public."users" 
    	WHERE users.name = p_name;
END;
$$;
