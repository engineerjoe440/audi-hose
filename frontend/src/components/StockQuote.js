import React from 'react';

function StockQuote(props) {


    return (
        <div className={'quote rounded-lg shadow-md p-4 bg-gray-800'}>
            <span className={'quoteSymbol text-sm text-white font-bold'}>{props.symbol}</span>
            <span className={'quoteSymbol text-2xs text-gray-400 ml-1'}>abc</span>
            <span className={'quoteSymbol text-2xs text-gray-400 ml-1'}>(def)</span>
            <div className={'quote flex flex-row justify-between mt-1'}>
                <div className={'quotePrice self-center text-2xl font-bold items-center text-white'}>$1.00</div>
                <div className={'flex flex-col text-right'}>
                    <div className={'quoteVar text-green-500'}>10%</div>
                    <div className={'quoteTime text-right text-2xs text-gray-400'}>5</div>
                </div>
            </div>
        </div>
    );
}

export default StockQuote;