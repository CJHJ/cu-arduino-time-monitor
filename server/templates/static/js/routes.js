import React from 'react';
import { HashRouter, Route } from 'react-router-dom';
import Home from './components/Home';
// import more components
export default (
    <HashRouter>
        <div>
            <Route path='/' component={Home} />
        </div>
    </HashRouter>
);