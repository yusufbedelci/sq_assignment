-- SQLite
SELECT name || ' ' || lastname AS fullname, user_id AS  id, email,password, mobile, age, gender, weight 
FROM user INNER JOIN user_profile ON user.user_id = user_profile.profile_id
WHERE email='super@company.nl' AND password='test1234';