import re

with open('/home/coder/projects/notes/springjpa/jpanotes.md', 'r') as f:
    text = f.read()

replacements = [
    (r"📌 First, configure your database", r"First, configure your database"),
    (r"# 🗄️ DB_CONFIG", r"# DB_CONFIG"),
    (r"📌 Use `@Entity`", r"Use `@Entity`"),
    (r"💡 \*\*What’s happening here\?\*\*", r"**💡 What’s happening here?**"),
    (r"\* 🆔 `@Id`", r"* `@Id`"),
    (r"\* 🔄 `@GeneratedValue`", r"* `@GeneratedValue`"),
    (r"\* ⏱️ `@CreationTimestamp`", r"* `@CreationTimestamp`"),
    (r"📌 This interface helps", r"This interface helps"),
    (r"💡 \*\*Built-in methods like:\*\*", r"**💡 Built-in methods like:**"),
    (r"📌 Now let’s fetch data", r"Now let’s fetch data"),
    (r"\* 🏗️ The JPA repository", r"* The JPA repository"),
    (r"\* 🧑‍💼 It uses `EntityManager`", r"* It uses `EntityManager`"),
    (r"\* 💾 When the `persist`", r"* When the `persist`"),
    (r"rolled back ↩️", r"rolled back."),
    (r"💡 Below snippet is very", r"**💡 Note:** Below snippet is very"),
    (r"❌ Output \*\*without\*\*", r"Output **without**"),
    (r"✅ Snippet two \*\*with\*\*", r"Snippet two **with**"),
    (r"🎯 Output\n!\[alt text\]", r"Output\n![alt text]"),
    (r"👀 Now here if you see", r"Now here if you see"),
    (r"\*\*📖 Explanation:\*\*", r"**Explanation:**"),
    (r"\* 📛 \*\*`name`\*\*", r"* **`name`**"),
    (r"\* 🚫 \*\*`uniqueConstraints`\*\*", r"* **`uniqueConstraints`**"),
    (r"\* ⚡ \*\*`indexes`\*\*", r"* **`indexes`**"),
    (r"📌 \*\*Note:\*\*", r"**💡 Note:**"),
    (r"\*\*🎯  Extras - FlyWay migration tool\*\*", r"### 🛠️ Extras - FlyWay migration tool"),
    (r"👉 Flyway is", r"* Flyway is"),
    (r"👉 It ensures", r"* It ensures"),
    (r"👉 Each migration", r"* Each migration"),
    (r"👉 Flyway replaces", r"* Flyway replaces"),
    (r"### \*\*8. JPA Query Methods\*\*", r"### 🔍 8. JPA Query Methods"),
    (r"\| 🔑 Keyword \| 🧪 Sample Method \| 📄 JPQL Snippet \|", r"| Keyword | Sample Method | JPQL Snippet |"),
    (r"\*\*9. JPQL & `@Query`\*\*", r"## 📝 9. JPQL & `@Query`"),
    (r"\*\*updating the record in database\*\*", r"### 🔄 Updating the record in database"),
]

for src, dst in replacements:
    text = re.sub(src, dst, text)

with open('/home/coder/projects/notes/springjpa/jpanotes.md', 'w') as f:
    f.write(text)

