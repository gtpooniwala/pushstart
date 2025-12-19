import React from 'react';
import { render, screen } from '@testing-library/react';
import TaskList from '../src/components/TaskList';

// Mock the props
const mockProps = {
  tasks: [],
  onToggleTask: jest.fn(),
  onDeleteTask: jest.fn(),
  onAddTask: jest.fn(),
};

// Mock global fetch
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve([]),
  })
) as jest.Mock;

describe('TaskList', () => {
  it('renders without crashing', async () => {
    render(<TaskList {...mockProps} />);
    // Check for the "Add Task" button or input placeholder
    // We use findBy because the component might be loading initially
    expect(await screen.findByPlaceholderText(/Add a task.../i)).toBeInTheDocument();
  });
});
