import { configureStore } from '@reduxjs/toolkit';

export const store = configureStore({
  reducer: {
    // Nous ajouterons les reducers ici au fur et à mesure
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
