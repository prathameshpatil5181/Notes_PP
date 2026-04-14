# 🚀 Spring Boot JPA Setup Guide

## ⚙️ 1. Database Configuration

First, configure your database in `application.properties`

```properties
# DB_CONFIG

spring.datasource.url=jdbc:postgresql://localhost:5432/orbit
spring.datasource.username=admin
spring.datasource.password=mypassword

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=false
```

---

## 🧩 2. Create Entity Class

Use `@Entity` to map your class to a database table

```java
package com.orbyte.hospitalmvn.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.CreationTimestamp;
import java.time.LocalDateTime;

@Entity
public class Patient {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private long id;

    private String name;

    @CreationTimestamp
    @Column(columnDefinition = "DATE DEFAULT CURRENT_DATE")
    private LocalDateTime created_on;

    private String email;

    private String gender;

}
```

**💡 What’s happening here?**

* `@Id` → Primary key
* `@GeneratedValue` → Auto increment
* `@CreationTimestamp` → Auto set creation time

---

## 📦 3. Create JPA Repository

This interface helps you interact with the database easily

```java
package com.orbyte.hospitalmvn.repository;

import com.orbyte.hospitalmvn.entity.Patient;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PatientRespository extends JpaRepository<Patient, Long> {}
```

**💡 Built-in methods like:**

  * `findAll()`
  * `save()`
  * `deleteById()`

---

## 🧪 4. Test the Repository

Now let’s fetch data using a test class

```java
@SpringBootTest
public class PatientRepositoryTest {

    @Autowired
    private PatientRespository patientRespository;

    @Test
    public void testPatientRepository() {

        List<Patient> patientlist = patientRespository.findAll();

        System.out.print(patientlist);

    }

}
```
## ⚙️ 5. Internal JPA Working

* The JPA repository is implemented by the `SimpleJpaRepository` class
* It uses `EntityManager` under the hood

## ♻️ Entity Manager Lifecycle

![alt text](image.png)

* When the `persist` call is made, data is moved from **transient** to **persistent** state. After successful completion of the txn, data is stored in the DB, else it is rolled back.

**💡 Note:** Below snippet is very interesting for understanding the `@Transactional` behavior.

## 💱 6. Database Transactions

* **All or Nothing:** A transaction ensures a series of operations either fully succeed together or completely fail, maintaining consistency.
* **Auto Rollback:** If an exception occurs, JPA instantly un-does (rolls back) any changes, leaving the database unaffected.

     See below snippet to understand the difference using @Transactional and not

``` java
    public Patient getPatient(Long id){
        Patient p1 = patientRespository.findById(id).orElseThrow();
        Patient p2  = patientRespository.findById(id).orElseThrow();
        System.out.println(p1==p2);
        return p1;
    }
```

Output **without** `@Transactional`

![alt text](image-1.png)

Snippet two **with** `@Transactional`

``` java
    @Transactional
    public Patient getPatient(Long id) {
        Patient p1 = patientRespository.findById(id).orElseThrow();
        Patient p2 = patientRespository.findById(id).orElseThrow();
        System.out.println(p1 == p2);
        p1.setName("takla");
        return p1;
    }

```
Output
![alt text](image-2.png)

Now here if you see, only a single query to check the patient is executed, and the same object is returned!


### **🏷️ 7. More annotations on entity**

---

```java
@Table(
        name="Patient",
        uniqueConstraints = {
                @UniqueConstraint(name="unique_patient_email",columnNames = {"email"}),
                @UniqueConstraint(name="unique_email_and_name",columnNames = {"name","email"})

        },
        indexes={
              @Index(name = "email_idx",columnList = "email")
        }

)
```

**Explanation:**
* **`name`**: Explicitly sets the database table name to "Patient".
* **`uniqueConstraints`**: Prevents duplicate entries for the `email` column alone, and for the combination of `name` + `email`.
* **`indexes`**: Creates a database index on the `email` column to greatly speed up searches and lookups.

* `@Enumrated` - this tag can be used to store enum values in the database. By default, it stores the enum values as strings, but it can also be configured to store them as integers.

**💡 Note:** The `@Column` annotation has many options. You can check them by ctrl+clicking on the annotation in your IDE.

### 🛠️ Extras - FlyWay migration tool

* Flyway is a database migration tool used to manage schema changes using versioned SQL scripts.

* It ensures all environments (dev, test, prod) stay consistent and synchronized.

* Each migration file is applied in order and tracked in a history table.

* Flyway replaces manual DB updates and is safer than using Hibernate ddl-auto.

**Data seeding - can be done using adding some properties use google that time**

### **🔍 8. JPA Query Methods**

---

Jpa query method help us to query the data in db using simple class methods. we donot have to manually create the data base queries.

for more method visit the doc: http://docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html

examples:  **List<User> findByEmailAddressAndLastname(String emailAddress, String lastname);**

| Keyword | Sample Method | JPQL Snippet |
|-----------|----------------|----------------|
| Distinct  | findDistinctByLastnameAndFirstname | select distinct … where x.lastname = ?1 and x.firstname = ?2 |
| And       | findByLastnameAndFirstname        | … where x.lastname = ?1 and x.firstname = ?2 |
| Or        | findByLastnameOrFirstname         | … where x.lastname = ?1 or x.firstname = ?2 |


## **📝 9. JPQL & `@Query`**

**JPQL**

* Object-based query language (works on entities, not tables).
Database-independent, used with JPA.
* @Query Used in Spring Data JPA to write custom JPQL/SQL queries.
Helps handle complex queries beyond method names.

```java
@Query("SELECT p from Patient p where p.bloodGroup=?1") // jpql
List<Patient> findByBloodGroup(@Param("bloodGroup") String bloodGroup);
```

**Group by query (Non-idea method)**
```java
@Query("SELECT p.bloodGroup, count(p.name) from Patient p GROUP BY p.bloodGroup")
List<Object[]> countByBloodGroup();
```

**Native Query**

Used to tell the jpa to run the query as its in `@Query` annotation.
use the `nativeQuery=true` attribute. 

```java
@Query(value = "SELECT * FROM Patient", nativeQuery = true)
List<Patient> findAllPatients();
```
### 🔄 Updating the record in database

To update the record in datebase we need use below 2 annotation along with `@query`


* `@Modifying` - this tells jpa that this query is modifying record
* `@Transactional` - this is a transaction inside the db if not done jpa will throw the error

e.g.

```java
@Transactional
@Modifying
@Query("UPDATE Patient p SET p.name=:name WHERE p.id=:id ")
int updateNameWithId(@Param("name") String name,@Param("id") Long id);
```

**DTO Projection**

This helps in matching the fetched data with your DTO. In this method you create the DTO and provide its reference to the repository and return data will be casted in that to format

e.g.

```java 
@Query("SELECT new com.orbyte.hospitalmvn.dto.BloodGroupCountResponseDTO(p.bloodGroup, count(p.name)) from Patient p GROUP BY p.bloodGroup")
List<BloodGroupCountResponseDTO> countByBloodGroup();
```

Output
```bash
Hibernate: select p1_0.blood_group,count(p1_0.name) from patient p1_0 group by p1_0.blood_group
[BloodGroupCountResponseDTO(BloodGroup=A_POSITIVE, count=2), BloodGroupCountResponseDTO(BloodGroup=AB_POSITIVE, count=1), BloodGroupCountResponseDTO(BloodGroup=O_POSITIVE, count=2)]
```

## Pagination with Pageable

Pegeable is a springboot class that deal with page data. It help us to fetch the data in page wise.

example 

```Java
@Query(value = "SELECT * FROM Patient", nativeQuery = true)
Page<Patient> findAllPatients(Pageable pageable);

 public void testFindAllPatientsNativeQuery(){
     Page<Patient>page = patientRespository.findAllPatients(PageRequest.of(0,2));

    for (Patient patient : page) {
        System.out.println(patient);
    }

}

```

output 
``` bash
Hibernate: SELECT * FROM Patient fetch first ? rows only
Hibernate: select count(1) FROM Patient
Patient{id=2, name='Diya Patel', created_on=2026-04-12T21:43:04.235602, email='diya.patel@example.com', gender='FEMALE'}
Patient{id=3, name='Dishant Verma', created_on=2026-04-12T21:43:04.235602, email='dishant.verma@example.com', gender='MALE'}

```