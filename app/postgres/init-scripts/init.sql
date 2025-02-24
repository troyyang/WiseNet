-- Sample SQL initialization script
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    mobile VARCHAR(20) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'USER',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP
);

INSERT INTO users (username, email, mobile, hashed_password, role) VALUES ('admin', 'troy.yang2@gmail.com', '', '21232f297a57a5a743894a0e4a801fc3', 'ADMIN');


-- init knowledge_lib
CREATE TABLE IF NOT EXISTS knowledge_lib (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- init knowledge_lib_subject
CREATE TABLE knowledge_lib_subject (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    knowledge_lib_id INTEGER REFERENCES knowledge_lib(id) ON DELETE CASCADE,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- init knowledge_lib
INSERT INTO knowledge_lib (id, title, content) VALUES
(1, 'Logistics and transportation', 'Logistics and transportation is the core business activity in modern commerce, involving the entire supply chain process from product production to the final consumption of the end customer. This field relies on efficient and accurate transportation systems to ensure that goods can be delivered to their intended destination in the shortest possible time and at the lowest cost. Logistics transportation does not just involve public road, rail, air, and water transportation, but also includes advanced information technology, supply chain management, and reasonable inventory policies. By optimizing routes, improving vehicle efficiency, implementing intelligent queuing systems, and utilizing real-time tracking, logistics transportation can significantly improve service quality, meet the growing demand for global trade. In addition, sustainable logistics practices are also being increasingly adopted to reduce environmental impact and achieve sustainable supply chains.');

-- init knowledge_lib_subject
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES 
(1, 'What goods are transported on the trunk line?', 1); 
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (2, 'What types of trucks are used in logistics?', 1); 
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (3, 'Logistics transportation process', 1); 
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (4, 'Which types of goods are transported by different types of trucks?', 1); 

-- init knowledge_lib
INSERT INTO knowledge_lib (id, title, content) VALUES
(2, 'Electronic commerce customer service industry', 'The electronic commerce customer service industry is a multifaceted field that plays a pivotal role in modern commerce, with its focus on the entire supply chain process from product production to the final consumption of the end customer. This field relies on efficient and accurate transportation systems to ensure that goods can be delivered to their intended destination in the shortest possible time and at the lowest cost. Logistics transportation does not just involve public road, rail, air, and water transportation, but also includes advanced information technology, supply chain management, and reasonable inventory policies. By optimizing routes, improving vehicle efficiency, implementing intelligent queuing systems, and utilizing real-time tracking, logistics transportation can significantly improve service quality, meet the growing demand for global trade. In addition, sustainable logistics practices are also being increasingly adopted to reduce environmental impact and achieve sustainable supply chains.');

-- init knowledge_lib_subject
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (5, 'Which industries are suitable for e-commerce customer service', 2); 
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (6, 'Electronic commerce customer service process', 2); 
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (8, 'Electronic commerce customer service communication skills', 2);

-- init knowledge_lib
INSERT INTO knowledge_lib (id, title, content) VALUES
(3, 'Weight Loss', 'Weight loss is the process of reducing body weight through a combination of diet and exercise. It aims to reduce the total amount of body fat while maintaining or increasing muscle mass. Weight loss can lead to improved health, reduced risk of chronic diseases, and increased overall well-being. It is an important goal for many individuals, especially those seeking to lose weight for various reasons, such as weight management, fitness, or overall health improvement.');

-- init knowledge_lib_subject
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (9, 'The Secret to Sustainable Weight Loss', 3); 
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (10, 'Weight Loss Diet', 3); 
INSERT INTO knowledge_lib_subject (id, name, knowledge_lib_id) VALUES (11, 'Weight Loss Exercise', 3);