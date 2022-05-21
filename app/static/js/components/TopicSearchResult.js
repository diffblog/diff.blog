'use strict';

import React, { useState, useEffect } from 'react';

import { TopicFollowButton } from './TopicFollowButton';

export function TopicSearchResult ({topicId, topicDisplayName, topicURL}) {
    return <div className="flex mb-4 items-center">
        <div className="ml-2">
            <a className="text-gray-900 font-bold text-base" href={topicURL}>
                { topicDisplayName}
            </a>
        </div>
        <TopicFollowButton topicId={topicId} />
    </div>
}
