import instance from './axios';

const uploads = async (data: FormData) => {
   return (await instance.post('/images/uploads', data)).data;
};

const getImages = async () => {
   return (await instance.get('/images')).data;
};

const getImageById = async (id: string) => {
   const response = await instance.get(`/images/${id}`, {
      responseType: 'blob',
   });

   return URL.createObjectURL(response.data);
};

const deleteImageById = async (id: string) => {
   return (await instance.delete(`images/${id}`)).data;
};

const updateImageById = async (id: string, data: unknown) => {
   return (await instance.put(`images/${id}`, data)).data;
};

export { uploads, getImages, getImageById, updateImageById, deleteImageById };
