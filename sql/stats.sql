# List publishers and counts
SELECT publisher, COUNT(id) FROM cards GROUP BY publisher;

# List type and counts
SELECT type, COUNT(id) FROM cards GROUP BY type;