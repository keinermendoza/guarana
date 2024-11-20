import { useState, useEffect } from "react";

export default function useFetch(url) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [data, setData] = useState(null);

    useEffect(() => {
        const controller = new AbortController();
        
        const fetchData = async () => {
            try {
                setLoading(true);
                setError('');
                const resp = await fetch(url, controller);
                if (!resp.ok) {throw new Error('Teve um erro')}
                
                const Data = await resp.json();
                setData(Data);
        
            } catch (err) {
                setError(err);
            } finally {
                setLoading(false);
            }

            return () => {
                controller.abort();
            }
        }
        fetchData();

    },[url])
    return {data, loading, error};
}
