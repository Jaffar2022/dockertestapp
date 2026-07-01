import './App.css';
import UserList from './components/UserList';
import { useState, useEffect } from 'react';
import UserForm from './components/UserForm';
import api from "./services/api";

function App() {

  const usersEndpoint = "/users";

  const [users, setUsers] = useState([]);
  const [error, setError] = useState("");

  // ----------------------------------
  // Fetch Users
  // ----------------------------------

  const fetchUsers = async () => {
    try {
      const { data } = await api.get(usersEndpoint);
      setUsers(data);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Could not fetch users!");
    }
  };

  // ----------------------------------
  // Add User
  // ----------------------------------

  const handleAddUser = async (name) => {
  try {
    const newUser = { name };

    const { data } = await api.post(usersEndpoint, newUser);

    setUsers((prevUsers) => [...prevUsers, data]);
    setError("");
  } catch (err) {
    console.error("Full Error:", err);

    if (err.response) {
      console.log("Status:", err.response.status);
      console.log("Response:", err.response.data);
    }

    setError("Could not add user!");
  }
};

  // ----------------------------------
  // Delete User
  // ----------------------------------

  const handleDeleteUser = async (user) => {

    try {

      // Remove immediately from UI
      setUsers(prevUsers =>
        prevUsers.filter(u => u._id !== user._id)
      );

      await api.delete(`${usersEndpoint}/${user._id}`);

      setError("");

    } catch (err) {

      console.error(err);

      setError("Could not delete user!");

      // Reload from backend if delete fails
      fetchUsers();
    }
  };

  // ----------------------------------
  // Initial Load
  // ----------------------------------

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div className="App">

      <UserForm onAddUser={handleAddUser} />

      {error && (
        <p role="alert" className="Error">
          {error}
        </p>
      )}

      <UserList
        users={users}
        onDeleteUser={handleDeleteUser}
      />

    </div>
  );
}

export default App;