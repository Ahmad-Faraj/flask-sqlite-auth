// API Configuration
const API_BASE_URL =
  window.location.hostname === "localhost" ? "http://localhost:5000" : "/api";

// Global state
let currentUser = null;
let currentPage = "login";

// Utility functions
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  const toastMessage = document.getElementById("toast-message");

  toast.className = `toast show ${type}`;
  toastMessage.textContent = message;

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

function showPage(pageName) {
  // Hide all pages
  document.querySelectorAll(".page").forEach((page) => {
    page.style.display = "none";
  });

  // Show selected page
  const page = document.getElementById(`${pageName}-page`);
  if (page) {
    page.style.display = "block";
    currentPage = pageName;

    // Load page-specific data
    switch (pageName) {
      case "dashboard":
        loadDashboardData();
        break;
      case "courses":
        loadCoursesData();
        break;
      case "grades":
        loadGradesData();
        break;
      case "profile":
        loadProfileData();
        break;
    }
  }
}

function showTab(tabName) {
  // Hide all tab contents
  document.querySelectorAll(".tab-content").forEach((tab) => {
    tab.style.display = "none";
  });

  // Remove active class from all tab buttons
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.classList.remove("active");
  });

  // Show selected tab
  document.getElementById(tabName).style.display = "block";

  // Add active class to clicked button
  event.target.classList.add("active");

  // Load tab-specific data
  if (tabName === "available-courses") {
    loadAvailableCourses();
  } else if (tabName === "my-courses") {
    loadMyCourses();
  }
}

// API functions
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const config = {
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }

    return data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
}

// Authentication functions
async function login(username, password) {
  try {
    const response = await apiRequest("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });

    currentUser = response.user;
    document.getElementById(
      "user-name"
    ).textContent = `Welcome, ${currentUser.first_name}`;
    document.getElementById("navbar").style.display = "block";
    showPage("dashboard");
    showToast("Login successful!", "success");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function register(formData) {
  try {
    const response = await apiRequest("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(formData),
    });

    showToast("Account created successfully! Please login.", "success");
    showPage("login");
  } catch (error) {
    showToast(error.message, "error");
  }
}

async function logout() {
  try {
    await apiRequest("/api/auth/logout", {
      method: "POST",
    });

    currentUser = null;
    document.getElementById("navbar").style.display = "none";
    showPage("login");
    showToast("Logged out successfully", "success");
  } catch (error) {
    showToast("Logout failed", "error");
  }
}

// Dashboard functions
async function loadDashboardData() {
  try {
    // Load student profile
    const profile = await apiRequest("/api/students/profile");
    document.getElementById(
      "student-id-display"
    ).textContent = `ID: ${profile.student_id}`;
    document.getElementById(
      "gpa-display"
    ).textContent = `GPA: ${profile.gpa.toFixed(2)}`;

    // Load course count
    const myCourses = await apiRequest("/api/courses/my-courses");
    document.getElementById(
      "course-count"
    ).textContent = `${myCourses.length} enrolled`;
  } catch (error) {
    console.error("Error loading dashboard:", error);
  }
}

// Courses functions
async function loadCoursesData() {
  loadAvailableCourses();
}

async function loadAvailableCourses() {
  try {
    const courses = await apiRequest("/api/courses/");
    const container = document.getElementById("available-courses-grid");

    container.innerHTML = courses
      .map(
        (course) => `
            <div class="course-card">
                <div class="course-header">
                    <span class="course-code">${course.course_code}</span>
                    <span class="course-credits">${
                      course.credits
                    } credits</span>
                </div>
                <div class="course-title">${course.title}</div>
                <div class="course-professor">
                    Professor: ${
                      course.professor ? course.professor.full_name : "TBA"
                    }
                </div>
                <div class="course-professor">
                    ${course.department} • ${course.semester} ${course.year}
                </div>
                <button class="btn btn-primary" onclick="enrollInCourse(${
                  course.id
                })">
                    Enroll
                </button>
            </div>
        `
      )
      .join("");
  } catch (error) {
    console.error("Error loading courses:", error);
  }
}

async function loadMyCourses() {
  try {
    const enrollments = await apiRequest("/api/courses/my-courses");
    const container = document.getElementById("my-courses-grid");

    container.innerHTML = enrollments
      .map((enrollment) => {
        const course = enrollment.course;
        return `
                <div class="course-card">
                    <div class="course-header">
                        <span class="course-code">${course.course_code}</span>
                        <span class="course-credits">${
                          course.credits
                        } credits</span>
                    </div>
                    <div class="course-title">${course.title}</div>
                    <div class="course-professor">
                        Professor: ${
                          course.professor ? course.professor.full_name : "TBA"
                        }
                    </div>
                    <div class="course-professor">
                        Status: ${enrollment.status}
                    </div>
                </div>
            `;
      })
      .join("");
  } catch (error) {
    console.error("Error loading my courses:", error);
  }
}

async function enrollInCourse(courseId) {
  try {
    await apiRequest(`/api/courses/${courseId}/enroll`, {
      method: "POST",
    });

    showToast("Enrolled successfully!", "success");
    loadAvailableCourses();
    loadDashboardData(); // Update course count
  } catch (error) {
    showToast(error.message, "error");
  }
}

// Grades functions
async function loadGradesData() {
  try {
    const grades = await apiRequest("/api/grades/my-grades");
    const container = document.getElementById("grades-content");

    if (Object.keys(grades).length === 0) {
      container.innerHTML =
        '<p style="text-align: center; color: #4a5568;">No grades available yet.</p>';
      return;
    }

    container.innerHTML = Object.entries(grades)
      .map(
        ([courseCode, courseData]) => `
            <div class="course-grades">
                <h3>${courseCode} - ${courseData.course.title}</h3>
                ${
                  courseData.grades.length > 0
                    ? `
                    <table class="grades-table">
                        <thead>
                            <tr>
                                <th>Assignment</th>
                                <th>Type</th>
                                <th>Score</th>
                                <th>Grade</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${courseData.grades
                              .map(
                                (grade) => `
                                <tr>
                                    <td>${grade.assignment_name}</td>
                                    <td>${grade.assignment_type}</td>
                                    <td>${grade.grade_value}/${
                                  grade.max_points
                                }</td>
                                    <td>
                                        <span class="grade-badge grade-${grade.letter_grade.toLowerCase()}">
                                            ${grade.letter_grade}
                                        </span>
                                    </td>
                                    <td>${new Date(
                                      grade.date_recorded
                                    ).toLocaleDateString()}</td>
                                </tr>
                            `
                              )
                              .join("")}
                        </tbody>
                    </table>
                `
                    : '<p style="color: #4a5568;">No grades recorded for this course yet.</p>'
                }
            </div>
        `
      )
      .join("");
  } catch (error) {
    console.error("Error loading grades:", error);
  }
}

// Profile functions
async function loadProfileData() {
  try {
    const profile = await apiRequest("/api/students/profile");
    const user = profile.user;

    document.getElementById("profile-first-name").value = user.first_name;
    document.getElementById("profile-last-name").value = user.last_name;
    document.getElementById("profile-email").value = user.email;
    document.getElementById("profile-major").value = profile.major;
    document.getElementById("profile-year-level").value = profile.year_level;
  } catch (error) {
    console.error("Error loading profile:", error);
  }
}

async function updateProfile(formData) {
  try {
    await apiRequest("/api/students/profile", {
      method: "PUT",
      body: JSON.stringify(formData),
    });

    showToast("Profile updated successfully!", "success");
    loadDashboardData(); // Refresh dashboard data
  } catch (error) {
    showToast(error.message, "error");
  }
}

// Event listeners
document.addEventListener("DOMContentLoaded", function () {
  // Hide navbar initially
  document.getElementById("navbar").style.display = "none";

  // Show login page initially
  showPage("login");

  // Login form
  document
    .getElementById("login-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      login(formData.get("username"), formData.get("password"));
    });

  // Signup form
  document
    .getElementById("signup-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const data = {
        username: formData.get("username"),
        email: formData.get("email"),
        password: formData.get("password"),
        first_name: formData.get("first_name"),
        last_name: formData.get("last_name"),
        major: formData.get("major") || "Undeclared",
        year_level: formData.get("year_level"),
        role: "student",
      };
      register(data);
    });

  // Profile form
  document
    .getElementById("profile-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const data = {
        first_name: formData.get("first_name"),
        last_name: formData.get("last_name"),
        email: formData.get("email"),
        major: formData.get("major"),
        year_level: formData.get("year_level"),
      };
      updateProfile(data);
    });

  // Check if user is already logged in
  checkAuth();
});

async function checkAuth() {
  try {
    const response = await apiRequest("/api/auth/me");
    currentUser = response.user;
    document.getElementById(
      "user-name"
    ).textContent = `Welcome, ${currentUser.first_name}`;
    document.getElementById("navbar").style.display = "block";
    showPage("dashboard");
  } catch (error) {
    // User not logged in, stay on login page
    showPage("login");
  }
}
