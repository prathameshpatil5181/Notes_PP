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

## **📄 9. Pagination with Pageable**

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

## **🔗 10. Defining relations** 

Owning side: the entity that owns the relation and cannot exits without inverse side. for e.g. appointment cannot exitst without the patient and doctor.

Inverse side: the entity that is in the other side of the relation. for e.g. patient and doctor are in the other side of the relation.

#### Relationship between owning side and inverse side

* the owning side detectes the foreign key updates
* updates on the mapped feild on inverse side cannot update the foreign key. 
* Parent controlls the lifecycle. here if patient is deleted their appointment will also be deleted. Hence Patient is Parent


#### 1. One to one relation 

One to one can be defined using the `@OneToOne` annotation. use the annotation on both the side.

e.g.

```java

// owning side here patient class
@OneToOne
@JoinColumn(name="patient_insurance_id")
private Insurance insurance;

// inverse side here insurance class
@OneToOne(mappedBy = "insurance")
private Patient patient;
```

**💡 Note:** 
* There will always only one owning side in One-to-One relation.
* **the class which we will use the `@JoinColumn` annotation is the owning side.**

#### 2. One to Many relation

To define the one to many relation we use the `@OneToMany` annotation and `@ManyToOne` annotation.

* `@OneToMany`:used on inverse side (one doctor can have many appointment)
* `@ManyToOne`:used on owning side  (many appointment can can belong one doctor)
 

e.g. 

```java
// inverse side here doctor class
@OneToMany(mappedBy = "doctor")
private List<Appointment> appointments =  new ArrayList<>(); // using arralist as we wil have many appointements

// owning side here appointment class
@ManyToOne
@JoinColumn(name = "docter_id",nullable = false)
private Doctor doctor;
```

**💡 Note:** 
* **There could be one or more relatation between the two tables.**

#### 3. Many to Many relation

Many to Many relation can be defined using the `@ManyToMany` annotation on both the side.

see below tags and implementation

example.

```java
// Owning side 
@ManyToMany
@JoinTable(
        name = "department_members",
        joinColumns = @JoinColum(name="dep_id"),
        inverseJoinColumns = @JoinColum(name = "doctor_id")
)
private Set<Doctor> doctors = new HashSet<();


// inverse side
@ManyToMany(mappedBy = "doctors")
private Set<Department> departments = newHashSet<>();


```

## **🌊 11. Cascading**


Cascading helps to persist the data in child entity to maintain the data in db. 
it automatically persist the data in child entity when the data is persisted in parent entity. and deletes as well in case of deletion in parent entity.

example

```java
@OneToOne(cascade = {CascadeType.MERGE,CascadeType.PERSIST})
@JoinColumn(name="patient_insurance_id")
private Insurance insurance;


public Patient assignInsuranceToPatient(@NonNull Long id, Insurance insurance){
    Patient patient = patientRespository.findById(id).orElseThrow(()->newRuntimeException("Patiend with Id " + id + " does not exists" ));
    patient.setInsurance(insurance); // dirty checking
    insurance.setPatient(patient); // birectional consistency
    return patient;
}
```

output:

```bash
Hibernate: select p1_0.id,p1_0.birth_date,p1_0.blood_group,p1_0.created_on,p1_0.email,p1_0.gender,i1_0.id,i1_0.created_at,i1_0.policy_number,i1_0.provider,i1_0.valid_until,p1_0.name from patient p1_0 left join insurance i1_0 on i1_0.id=p1_0.patient_insurance_id where p1_0.id=?
Hibernate: insert into insurance (created_at,policy_number,provider,valid_until) values (?,?,?,?)
Hibernate: update patient set birth_date=?,blood_group=?,email=?,gender=?,patient_insurance_id=?,name=? where id=?
```
if you analayze the above output. you can see the once data in patient is added there is automatic creation of the entry in insurance table.


#### In JPA, cascading tells the persistence provider (like Hibernate) what operations to propagate from to its related child entities automatically.

* CascadeType.PERSI5T: Propagate persist (save) operation.
* CascadeType.MERGE: Propagate merge (update) operation.
* CascadeType.REMOVE: Propagate remove (delete) operation.
* CascadeType.REFRESH: Propagate refresh operation.
* CascadeType.DETACH: Propagate detach operation.
* CascadeType.ALL: Propagate all operations (PERSIST, MERGE, REMOVE, REFRESH, DETACH).


#### Key Points About orphanRemoval

* **When It Tri ggers:**
    * For OneToMany: When an entity is removed from the collection (e.g., List.remove(), clear(), or reassigning a new collection).
    * For OneToOne: When the reference is set to null or replaced with a new entity.
* **Automatic Deletion:**
    * Orphaned entities are deleted automatically during the JPA flush or commit operation, without needing explicit calls to entity.remove()
* **Difference from CascadeType.REMOVE:**
    * CascadeType.REMOVE deletes child entities only when the parent is deleted.
    * orphanRemoval = true deletes child entities when they are no longer referenced by the parent remains in the database.
* **Use Case:**
    * Ideal for relationships where the child entity has no meaning without the parent (e.g., an Appointment without a Doctor or Patient, or an Insurance without a Patient) 



---

## **🎯 12. Fetch Types — LAZY vs EAGER** *(Interview Favourite)*

Controls **when** related entities are loaded from DB.

| Type | Loads | Default For |
|------|-------|-------------|
| `EAGER` | Immediately with parent | `@ManyToOne`, `@OneToOne` |
| `LAZY`  | Only when accessed | `@OneToMany`, `@ManyToMany` |

```java
@OneToMany(mappedBy = "doctor", fetch = FetchType.LAZY)
private List<Appointment> appointments;
```

**💡 Interview Points:**
* Always prefer `LAZY` — avoids loading unnecessary data
* `LAZY` uses **proxy objects** (Hibernate creates a subclass)
* Accessing lazy field **outside** a transaction → `LazyInitializationException`
* EAGER can cause **performance issues** with large datasets

---

## **⚠️ 13. N+1 Problem** *(Very Common Interview Question)*

**What:** 1 query to fetch N parents + N extra queries to fetch each parent's children = **N+1 queries total**.

**When:** Happens with `LAZY` fetch when you loop through parent and access children.

```java
// BAD — triggers N+1
List<Doctor> doctors = doctorRepo.findAll();       // 1 query
for (Doctor d : doctors) {
    d.getAppointments().size();                    // N queries (1 per doctor)
}
```

**3 Solutions:**

**1. JOIN FETCH (JPQL)**
```java
@Query("SELECT d FROM Doctor d JOIN FETCH d.appointments")
List<Doctor> findAllWithAppointments();
```

**2. @EntityGraph**
```java
@EntityGraph(attributePaths = {"appointments"})
List<Doctor> findAll();
```

**3. Batch Fetching (Hibernate)**
```properties
spring.jpa.properties.hibernate.default_batch_fetch_size=20
```

---

## **🗄️ 14. Caching in JPA/Hibernate**

### First Level Cache (L1)
* **Enabled by default**, cannot be disabled
* Scope: **per session/transaction**
* Same entity fetched twice in one txn → only 1 DB query
* This is why `p1 == p2` was `true` with `@Transactional` (section 6 above)

### Second Level Cache (L2)
* **Not enabled by default**, needs config
* Scope: **across sessions** (shared by all users)
* Needs provider like **EhCache** or **Redis**
* Use `@Cacheable` on entity to enable

```java
@Entity
@Cacheable
@org.hibernate.annotations.Cache(usage = CacheConcurrencyStrategy.READ_WRITE)
public class Patient { }
```

**💡 Interview Point:** L1 cache is why Hibernate returns same object reference inside a transaction. L2 cache is for app-wide performance boost.

---

## **🔄 15. Entity Lifecycle States** *(Interview Favourite)*

| State | In Context? | In DB? | How to reach |
|-------|-------------|--------|--------------|
| **Transient** | ❌ | ❌ | `new Patient()` |
| **Persistent** | ✅ | ✅ | `em.persist()` or `repo.save()` |
| **Detached** | ❌ | ✅ | After txn closes or `em.detach()` |
| **Removed** | ✅ | ❌ (pending) | `em.remove()` or `repo.delete()` |

**💡 Key Points:**
* **Persistent** objects are tracked — any field change is auto-synced to DB (dirty checking)
* **Detached** objects are NOT tracked — changes are ignored unless you `merge()` them back
* `save()` on a detached entity → Hibernate does `merge()` internally

---

## **🔍 16. Dirty Checking**

* Hibernate **automatically detects changes** to persistent entities
* At flush/commit time → compares current state vs snapshot taken at load time
* If changed → generates UPDATE query **without you calling save()**

```java
@Transactional
public void updateName(Long id, String name) {
    Patient p = repo.findById(id).orElseThrow();
    p.setName(name);     // NO save() needed! Hibernate auto-updates at txn end
}
```

**💡 Interview Point:** This only works inside `@Transactional`. Without it, entity is detached and changes are lost.

---

## **💱 17. @Transactional Deep Dive** *(Interview Must-Know)*

### Propagation Types
Controls what happens when a transactional method calls another transactional method.

| Type | Behaviour |
|------|-----------|
| `REQUIRED` (default) | Join existing txn, or create new if none |
| `REQUIRES_NEW` | Always create new txn, suspend current |
| `MANDATORY` | Must run inside existing txn, else exception |
| `NESTED` | Create savepoint inside current txn |
| `NOT_SUPPORTED` | Suspend txn and run non-transactionally |
| `NEVER` | Throw exception if txn exists |

### Isolation Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|-----------|-------------------|-------------|
| `READ_UNCOMMITTED` | ✅ | ✅ | ✅ |
| `READ_COMMITTED` | ❌ | ✅ | ✅ |
| `REPEATABLE_READ` | ❌ | ❌ | ✅ |
| `SERIALIZABLE` | ❌ | ❌ | ❌ |

```java
@Transactional(propagation = Propagation.REQUIRES_NEW, isolation = Isolation.READ_COMMITTED)
public void transferFunds() { }
```

**💡 Interview Points:**
* `@Transactional` works via **AOP proxy** — calling a `@Transactional` method from within the **same class** bypasses the proxy → **txn won't apply**
* By default rolls back on **unchecked exceptions** only. Use `rollbackFor = Exception.class` to include checked exceptions
* Place `@Transactional` on **service layer**, not on controller or repository

---

## **🔐 18. Locking** *(Interview Important)*

### Optimistic Locking
* Uses a `@Version` field — no DB locks held
* On update, checks if version matches → if not, throws `OptimisticLockException`
* Best for **read-heavy** apps with rare conflicts

```java
@Entity
public class Patient {
    @Version
    private Integer version;
}
```

### Pessimistic Locking
* Actually locks the DB row — other txns must wait
* Best for **write-heavy** apps where conflicts are frequent

```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("SELECT p FROM Patient p WHERE p.id = :id")
Patient findByIdWithLock(@Param("id") Long id);
```

**💡 Interview Point:** Optimistic = version check at commit time (no DB lock). Pessimistic = DB row lock immediately (blocks other txns).

---

## **📋 19. JPA Auditing**

Auto-track who created/modified a record and when.

**Step 1:** Enable auditing
```java
@Configuration
@EnableJpaAuditing
public class JpaConfig { }
```

**Step 2:** Add audit fields
```java
@Entity
@EntityListeners(AuditingEntityListener.class)
public class Patient {

    @CreatedDate
    private LocalDateTime createdAt;

    @LastModifiedDate
    private LocalDateTime updatedAt;

    @CreatedBy
    private String createdBy;

    @LastModifiedBy
    private String modifiedBy;
}
```

**💡 Tip:** For `@CreatedBy`/`@LastModifiedBy`, implement `AuditorAware<String>` interface to provide current user.

---

## **🏗️ 20. Inheritance Mapping Strategies** *(Interview Question)*

How to map Java class inheritance to DB tables.

| Strategy | Tables | Performance | Use When |
|----------|--------|-------------|----------|
| `SINGLE_TABLE` (default) | 1 table for all | Fastest (no joins) | Few subclass-specific fields |
| `JOINED` | 1 table per class | Slower (joins needed) | Many subclass fields, need normalization |
| `TABLE_PER_CLASS` | Separate table per concrete class | Slowest for polymorphic queries | Rarely used |

```java
@Entity
@Inheritance(strategy = InheritanceType.SINGLE_TABLE)
@DiscriminatorColumn(name = "person_type")
public class Person { }

@Entity
@DiscriminatorValue("DOCTOR")
public class Doctor extends Person { }

@Entity
@DiscriminatorValue("PATIENT")
public class Patient extends Person { }
```

**💡 Interview Point:** `SINGLE_TABLE` adds a discriminator column. `JOINED` is most normalized. `TABLE_PER_CLASS` avoids discriminator but duplicates parent columns.

---

## **📦 21. @Embeddable & @Embedded**

Group related fields into a reusable component **without creating a separate table**.

```java
@Embeddable
public class Address {
    private String street;
    private String city;
    private String pincode;
}

@Entity
public class Patient {
    @Embedded
    private Address address;  // street, city, pincode stored in Patient table
}
```

**💡 Interview Point:** Unlike `@Entity`, `@Embeddable` has **no own table, no own ID**. It's a value object embedded in parent table.

---

## **⚡ 22. Quick Interview Q&A**

**Q: JPA vs Hibernate vs Spring Data JPA?**
* **JPA** = Specification (set of interfaces/rules)
* **Hibernate** = Implementation of JPA (the actual engine)
* **Spring Data JPA** = Abstraction over Hibernate (auto-generates repo code)

**Q: `save()` vs `saveAndFlush()`?**
* `save()` → queues changes, writes at txn commit
* `saveAndFlush()` → writes to DB immediately

**Q: `findById()` vs `getById()` / `getReferenceById()`?**
* `findById()` → hits DB immediately, returns `Optional`
* `getReferenceById()` → returns a **proxy** (lazy), hits DB only when you access a field

**Q: What is `@MappedSuperclass`?**
* Base class that provides common fields (id, createdAt) to child entities
* **Not an entity** itself — no table created for it
* Unlike `@Inheritance`, no polymorphic queries possible

```java
@MappedSuperclass
public abstract class BaseEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @CreatedDate
    private LocalDateTime createdAt;
}
```

**Q: What is `spring.jpa.open-in-view`?**
* Default `true` — keeps Hibernate session open until HTTP response is sent
* Allows lazy loading in controller/view layer
* **Best practice:** Set to `false` and handle all DB access in service layer

**Q: Difference between `@JoinColumn` and `mappedBy`?**
* `@JoinColumn` → owning side, creates FK column in this table
* `mappedBy` → inverse side, no FK here, just reads from owning side



